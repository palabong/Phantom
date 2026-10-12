import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8000/sse/?token=ph_live_D2aZuYtdGL6tUfuV2egoxp"
TARGET_NAV_URL = "https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/15326172709092"
TARGET_VARIANT_ID = "67407288565988"

async def run():
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join("runs", f"prod_postdeploy_{utc_timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    print(f"[*] Run directory created: {run_dir}")
    print(f"[*] Connecting to local Phantom SSE server: {SSE_URL}")

    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] Session initialized successfully.")

            # --- Preflight Check: Confirm with one get_snapshot html first ---
            print("\n--- [Step 0] Preflight get_snapshot html ---")
            pre_snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
            pre_snap_text = pre_snap_res.content[0].text if pre_snap_res.content else ""
            print(f"[+] Preflight snapshot retrieved ({len(pre_snap_text)} characters).")

            with open(os.path.join(run_dir, "snapshot_preflight.html"), "w", encoding="utf-8") as f:
                f.write(pre_snap_text)

            # Check if challenge appears
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", pre_snap_text, re.I):
                print("[!] Challenge detected during preflight snapshot. Halting.")
                stop_path = os.path.join(run_dir, "STOP.txt")
                with open(stop_path, "w", encoding="utf-8") as f:
                    f.write("challenge\n")
                print(f"[!] Written {stop_path}. Exiting.")
                return

            # --- Step 1: navigate to Beanie product page (One navigation only) ---
            print(f"\n--- [Step 1] Navigate to {TARGET_NAV_URL} (One navigation only) ---")
            nav_res = await session.call_tool("navigate", {"url": TARGET_NAV_URL})
            nav_text = nav_res.content[0].text if nav_res.content else ""
            print(f"[+] Navigation completed: {nav_text}")

            # Allow hydration of Polaris UI
            print("[*] Waiting 4000ms for Polaris UI hydration...")
            await session.call_tool("wait", {"delay_ms": 4000})

            # --- Step 2: get_snapshot html ---
            print("\n--- [Step 2] get_snapshot html ---")
            post_snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
            post_snap_text = post_snap_res.content[0].text if post_snap_res.content else ""
            print(f"[+] Product page snapshot retrieved ({len(post_snap_text)} characters).")

            with open(os.path.join(run_dir, "snapshot_product_page.html"), "w", encoding="utf-8") as f:
                f.write(post_snap_text)

            # Check if challenge appeared after navigation
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", post_snap_text, re.I):
                print("[!] Challenge appeared after navigation. Halting.")
                stop_path = os.path.join(run_dir, "STOP.txt")
                with open(stop_path, "w", encoding="utf-8") as f:
                    f.write("challenge\n")
                print(f"[!] Written {stop_path}. Exiting.")
                return

            # --- Step 3: evaluate: extract inventory quantity for variant 67407288565988 (Green) ---
            print("\n--- [Step 3] evaluate: Extract inventory data ---")
            eval_js = r"""(() => {
                const title = document.title || "";
                const href = location.href || "";
                const bodyText = document.body ? document.body.innerText : "";

                // Total inventory detection
                let totalStock = null;
                const totalMatch = bodyText.match(/(\d+)\s+in\s+stock(?:\s+for\s+\d+\s+variants)?/i) || 
                                   bodyText.match(/(\d+)\s+available(?:\s+across\s+\d+\s+variants)?/i) ||
                                   bodyText.match(/Total\s+inventory[\s:]*(\d+)/i);
                if (totalMatch) {
                    totalStock = totalMatch[0];
                }

                // Table rows / variant list extraction
                const rows = Array.from(document.querySelectorAll('tr, [role="row"], .Polaris-IndexTable__TableRow, [data-polaris-unread]'));
                const variants = [];
                let targetVariant = null;

                for (const row of rows) {
                    const txt = (row.innerText || "").trim();
                    if (!txt) continue;

                    const cells = Array.from(row.querySelectorAll('td, th, [role="cell"], [role="gridcell"], input')).map(c => {
                        if (c.tagName === 'INPUT') return c.value || c.placeholder || "";
                        return (c.innerText || "").trim();
                    }).filter(Boolean);

                    const isTargetId = txt.includes('67407288565988') || (row.innerHTML && row.innerHTML.includes('67407288565988'));
                    const isGreen = /\bgreen\b/i.test(txt);

                    if (isGreen || isTargetId || /(?:olive|ocean|purple|red|black|blue|white|yellow)/i.test(txt)) {
                        const item = {
                            text: txt.replace(/\n+/g, ' | '),
                            cells: cells,
                            isTarget: isTargetId || isGreen
                        };
                        variants.push(item);
                        if (isTargetId || isGreen) {
                            targetVariant = item;
                        }
                    }
                }

                // Fallback check in HTML for variant ID link
                const html = document.documentElement.outerHTML || "";
                let targetIdFoundInHtml = html.includes('67407288565988');
                let targetLinkHref = null;
                const linkElem = document.querySelector('a[href*="67407288565988"]');
                if (linkElem) {
                    targetLinkHref = linkElem.getAttribute('href');
                }

                // Error banners check
                const errorElements = Array.from(document.querySelectorAll('[role="alert"], .Polaris-Banner--statusCritical, .Polaris-Banner--statusWarning'));
                const errors = errorElements.map(e => (e.innerText || "").trim()).filter(Boolean);

                return JSON.stringify({
                    pageTitle: title,
                    currentUrl: href,
                    totalStock: totalStock,
                    targetVariantId: '67407288565988',
                    targetVariant: targetVariant,
                    allVariants: variants,
                    targetIdFoundInHtml: targetIdFoundInHtml,
                    targetLinkHref: targetLinkHref,
                    errors: errors
                });
            })()"""

            eval_res = await session.call_tool("evaluate", {"expression": eval_js})
            raw_eval_text = eval_res.content[0].text if eval_res.content else "{}"
            
            # Parse evaluation result
            eval_data = json.loads(raw_eval_text)
            if isinstance(eval_data, str):
                eval_data = json.loads(eval_data)

            print("[+] Evaluation executed successfully:")
            print(json.dumps(eval_data, indent=2))

            # --- Step 4: Write outcome to run folder from evaluate only. Stop. ---
            print("\n--- [Step 4] Writing outcome to run folder ---")
            
            outcome_data = {
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "navigation_url": TARGET_NAV_URL,
                "page_title": eval_data.get("pageTitle"),
                "total_stock": eval_data.get("totalStock"),
                "target_variant_id": TARGET_VARIANT_ID,
                "target_variant_details": eval_data.get("targetVariant"),
                "all_detected_variants": eval_data.get("allVariants"),
                "target_link_href": eval_data.get("targetLinkHref"),
                "errors": eval_data.get("errors")
            }

            json_outcome_file = os.path.join(run_dir, "outcome.json")
            with open(json_outcome_file, "w", encoding="utf-8") as f:
                json.dump(outcome_data, f, indent=2)

            # Generate markdown summary
            target_v = eval_data.get("targetVariant")
            md_lines = [
                "# Beanie Product Inventory Outcome",
                f"- **Timestamp (UTC)**: `{outcome_data['timestamp_utc']}`",
                f"- **Product URL**: `{TARGET_NAV_URL}`",
                f"- **Page Title**: `{eval_data.get('pageTitle')}`",
                f"- **Total Stock Extracted**: `{eval_data.get('totalStock') or 'Not directly stated'}`",
                "",
                "## Target Variant: 67407288565988 (Green)",
                f"- **Variant ID**: `{TARGET_VARIANT_ID}`",
                f"- **Variant Details / Row**: `{target_v.get('text') if target_v else 'Not Found'}`",
                f"- **Extracted Cells**: `{json.dumps(target_v.get('cells') if target_v else [])}`",
                f"- **Direct Link**: `{eval_data.get('targetLinkHref') or 'N/A'}`",
                "",
                "## Per-Variant Stock List",
            ]

            if eval_data.get("allVariants"):
                for idx, v in enumerate(eval_data["allVariants"], 1):
                    md_lines.append(f"{idx}. **Row**: `{v.get('text')}`")
                    md_lines.append(f"   - **Cells**: `{v.get('cells')}`")
            else:
                md_lines.append("- No variant rows detected.")

            md_lines.extend([
                "",
                "## Errors / Banners",
                f"- **Errors**: {json.dumps(eval_data.get('errors', [])) or 'None'}"
            ])

            md_outcome_file = os.path.join(run_dir, "outcome.md")
            with open(md_outcome_file, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))

            print(f"[+] Outcome written to {json_outcome_file} and {md_outcome_file}")
            print("[+] Task finished. Stopping.")

if __name__ == "__main__":
    asyncio.run(run())
