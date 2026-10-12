import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_beanie_variant_inspect"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
PRODUCT_URL = "https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/15326172709092"
TARGET_VARIANT_ID = "67407288565988"

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to Local Phantom via SSE: {SSE_URL}...")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Session initialized.")
            
            # --- Pre-flight: Confirm with one get_snapshot html first ---
            print("\n[Pre-flight] Calling get_snapshot (mode='html')...")
            pre_snap = await session.call_tool("get_snapshot", {"mode": "html"})
            pre_text = pre_snap.content[0].text if pre_snap.content else ""
            
            with open(os.path.join(run_dir, "preflight_snapshot.txt"), "w") as f:
                f.write(pre_text)
                
            # Check for challenges
            is_challenge = bool(re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", pre_text, re.I))
            if is_challenge:
                print("[STOP] Challenge detected in preflight snapshot!")
                stop_file = os.path.join(run_dir, "STOP.txt")
                with open(stop_file, "w") as f:
                    f.write("challenge\n")
                return
                
            has_h1_staff = "H1 Staff" in pre_text or "palabong+staff@wearehackerone.com" in pre_text
            print(f"Preflight status: Authenticated as H1 Staff: {has_h1_staff}")
            
            # --- 1. navigate to https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/15326172709092 ---
            print(f"\n[Step 1] Navigating to {PRODUCT_URL} (one navigation only)...")
            nav_res = await session.call_tool("navigate", {"url": PRODUCT_URL})
            nav_text = nav_res.content[0].text if nav_res.content else ""
            print(f"Navigation result: {nav_text}")
            
            # Wait for Polaris product page and variant table hydration
            print("Waiting 4000ms for page hydration...")
            await session.call_tool("wait", {"delay_ms": 4000})
            
            # --- 2. get_snapshot html ---
            print("\n[Step 2] Calling get_snapshot (mode='html')...")
            snap2 = await session.call_tool("get_snapshot", {"mode": "html"})
            snap2_text = snap2.content[0].text if snap2.content else ""
            print(f"Step 2 snapshot length: {len(snap2_text)} chars")
            
            with open(os.path.join(run_dir, "product_page_snapshot.txt"), "w") as f:
                f.write(snap2_text)
                
            # Check if challenge appeared on product page
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", snap2_text, re.I):
                print("[STOP] Challenge appeared after navigation!")
                stop_file = os.path.join(run_dir, "STOP.txt")
                with open(stop_file, "w") as f:
                    f.write("challenge\n")
                return
                
            # --- 3. evaluate: extract the inventory quantity for variant 67407288565988 (Green) ---
            print("\n[Step 3] Calling evaluate to extract variant stock details...")
            eval_expr = """(() => {
                const title = document.title;
                const href = location.href;
                const bodyText = document.body ? document.body.innerText : "";
                
                // 1. Check for total inventory
                let totalStock = null;
                const totalMatch = bodyText.match(/(\\d+)\\s+in\\s+stock(?:\\s+for\\s+\\d+\\s+variants)?/i) || bodyText.match(/Total\\s+inventory[\\s:]*(\\d+)/i);
                if (totalMatch) totalStock = totalMatch[1] || totalMatch[0];
                
                // 2. Scan variant table rows / items
                const rows = Array.from(document.querySelectorAll('tr, [role="row"], .Polaris-IndexTable__TableRow, [data-polaris-unread]'));
                const variantsFound = [];
                let targetVariantInfo = null;
                
                for (const row of rows) {
                    const txt = row.innerText.trim();
                    if (!txt) continue;
                    
                    // Look for variant names or IDs
                    const isGreen = /green/i.test(txt);
                    const hasTargetId = txt.includes('67407288565988');
                    
                    // Look for numbers representing stock in cells
                    const cells = Array.from(row.querySelectorAll('td, th, [role="cell"], [role="gridcell"], input')).map(c => {
                        if (c.tagName === 'INPUT') return c.value || c.placeholder;
                        return c.innerText.trim();
                    }).filter(Boolean);
                    
                    if (isGreen || hasTargetId || /(?:black|blue|red|yellow|green|white|gray|small|medium|large)/i.test(txt)) {
                        const rowData = {
                            text: txt.replace(/\\n+/g, ' | '),
                            cells: cells,
                            isTarget: isGreen || hasTargetId
                        };
                        variantsFound.push(rowData);
                        if (isGreen || hasTargetId) {
                            targetVariantInfo = rowData;
                        }
                    }
                }
                
                // 3. Fallback: Search in entire HTML for target variant ID or Green inventory
                const html = document.documentElement.outerHTML;
                let htmlTargetMatch = null;
                const targetIdx = html.indexOf('67407288565988');
                if (targetIdx !== -1) {
                    htmlTargetMatch = html.slice(Math.max(0, targetIdx - 200), Math.min(html.length, targetIdx + 300));
                }
                
                // Fallback regex for Green stock in text
                const greenRegex = /Green[\\s\\S]{0,100}?(\\d+)(?:\\s*(?:available|in stock|on hand))?/i;
                const mGreen = bodyText.match(greenRegex);
                const greenStockText = mGreen ? mGreen[0].replace(/\\n+/g, ' ') : null;
                
                // 4. Check for any errors on the page
                const errorBanner = Array.from(document.querySelectorAll('[role="alert"], .Polaris-Banner--statusCritical')).map(e => e.innerText.trim());
                
                return JSON.stringify({
                    href: href,
                    title: title,
                    totalStock: totalStock,
                    targetVariantId: '67407288565988',
                    targetVariantInfo: targetVariantInfo,
                    greenStockText: greenStockText,
                    variantsFound: variantsFound,
                    htmlSnippetTarget: htmlTargetMatch,
                    errors: errorBanner,
                    bodySnippet: bodyText.slice(0, 1500)
                });
            })()"""
            
            eval_res = await session.call_tool("evaluate", {"expression": eval_expr})
            raw_eval = eval_res.content[0].text if eval_res.content else "{}"
            parsed_eval = json.loads(raw_eval)
            if isinstance(parsed_eval, str):
                try:
                    parsed_eval = json.loads(parsed_eval)
                except Exception:
                    pass
            print("\nEvaluation Result:")
            print(json.dumps(parsed_eval, indent=2))
            
            # --- 4. Write outcome to run folder from evaluate only. Stop. ---
            target_info = parsed_eval.get("targetVariantInfo")
            outcome_lines = [
                "# Beanie Product & Variant Inventory Outcome",
                f"- **Timestamp (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                f"- **Product URL**: `{PRODUCT_URL}`",
                f"- **Page Title**: `{parsed_eval.get('title')}`",
                f"- **Total Inventory**: {parsed_eval.get('totalStock') or 'Not directly stated'}",
                "",
                "## Target Variant Details (Variant 67407288565988 - Green)",
                f"- **Target Variant ID**: `67407288565988`",
                f"- **Target Variant Row**: `{target_info.get('text') if target_info else 'Not Found in Table Rows'}`",
                f"- **Target Variant Cells**: `{json.dumps(target_info.get('cells') if target_info else [])}`",
                f"- **Green Stock Text (Regex Extract)**: `{parsed_eval.get('greenStockText')}`",
                "",
                "## All Detected Variants & Stock",
            ]
            
            for v in parsed_eval.get("variantsFound", []):
                outcome_lines.append(f"- **Row**: `{v.get('text')}`")
                outcome_lines.append(f"  - **Cells**: `{v.get('cells')}`")
                
            outcome_lines.extend([
                "",
                "## HTML / Context Snippet around Variant ID",
                "```html",
                f"{parsed_eval.get('htmlSnippetTarget') or 'Variant ID not found in HTML source'}",
                "```",
                "",
                "## Page Errors",
                f"- **Errors**: {json.dumps(parsed_eval.get('errors', [])) or 'None'}",
                "",
                "## Body Preview",
                "```text",
                f"{parsed_eval.get('bodySnippet', '')[:800]}",
                "```"
            ])
            
            outcome_file = os.path.join(run_dir, "beanie_variant_inventory_outcome.md")
            with open(outcome_file, "w") as f:
                f.write("\n".join(outcome_lines))
            print(f"\n[DONE] Outcome successfully written to {outcome_file}")

if __name__ == "__main__":
    asyncio.run(main())
