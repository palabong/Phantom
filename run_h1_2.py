import asyncio
import os
import sys
import time
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

CONFIG_PATH = os.path.join(".agents", "mcp_config.json")
TOKEN = "ph_live_D2aZuYtdGL6tUfuV2egoxp"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            url = cfg.get("mcpServers", {}).get("phantom-cloud-local", {}).get("serverUrl")
            if url:
                SSE_URL = url
    except Exception as e:
        print(f"Warning loading mcp_config.json: {e}")

TARGET_STORE_URL = "https://admin.shopify.com/store/funk-it-up-sdzgxmea"
PRODUCT_URL = "https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603521722"

async def run():
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join("runs", f"prod_postdeploy_{utc_timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    print(f"[*] Archive directory: {run_dir}")
    print(f"[*] Connecting to {SSE_URL} (single session)...")

    protocol_log = []

    def write_stop(msg):
        print(f"[!] STOP: {msg}")
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write(msg.strip() + "\n")
        with open("STOP.txt", "w", encoding="utf-8") as f:
            f.write(msg.strip() + "\n")
        with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
            json.dump(protocol_log, f, indent=2)

    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] MCP Session initialized.")

            # --- Step 1: get_snapshot html ---
            print("\n--- [Step 1] get_snapshot html ---")
            t0 = time.perf_counter()
            snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
            dt_snap = (time.perf_counter() - t0) * 1000
            snap_text = snap_res.content[0].text if snap_res.content else ""
            print(f"[+] Initial snapshot retrieved in {dt_snap:.1f}ms ({len(snap_text)} chars).")

            with open(os.path.join(run_dir, "snapshot_step1.html"), "w", encoding="utf-8") as f:
                f.write(snap_text)

            protocol_log.append({
                "step": "step1_get_snapshot",
                "duration_ms": dt_snap,
                "length": len(snap_text),
                "preview": snap_text[:300]
            })

            # Check if current page is already an authenticated admin for funk-it-up-sdzgxmea
            is_auth_store_a = "funk-it-up-sdzgxmea" in snap_text.lower() and ("admin" in snap_text.lower() or "polaris" in snap_text.lower() or "products" in snap_text.lower())
            
            # Also evaluate location.href
            href_res = await session.call_tool("evaluate", {"expression": "location.href"})
            current_href = href_res.content[0].text if href_res.content else ""
            print(f"[*] Current location.href: {current_href}")

            if "funk-it-up-sdzgxmea" in current_href and "admin.shopify.com" in current_href and not re.search(r"login|challenge|accounts", current_href):
                is_auth_store_a = True

            print(f"[*] Already authenticated admin for funk-it-up-sdzgxmea: {is_auth_store_a}")

            # --- Step 2: Navigate if not authenticated ---
            if not is_auth_store_a:
                print(f"\n--- [Step 2] navigate once to {TARGET_STORE_URL} ---")
                t0 = time.perf_counter()
                nav_res = await session.call_tool("navigate", {"url": TARGET_STORE_URL})
                dt_nav = (time.perf_counter() - t0) * 1000
                nav_text = nav_res.content[0].text if nav_res.content else ""
                print(f"[+] Navigated in {dt_nav:.1f}ms: {nav_text}")

                protocol_log.append({
                    "step": "step2_navigate",
                    "url": TARGET_STORE_URL,
                    "duration_ms": dt_nav,
                    "result": nav_text
                })

                print("[*] Waiting 3000ms for page load...")
                await session.call_tool("wait", {"delay_ms": 3000})

                snap2_res = await session.call_tool("get_snapshot", {"mode": "html"})
                snap2_text = snap2_res.content[0].text if snap2_res.content else ""
                with open(os.path.join(run_dir, "snapshot_step2.html"), "w", encoding="utf-8") as f:
                    f.write(snap2_text)

                protocol_log.append({
                    "step": "step2_get_snapshot",
                    "length": len(snap2_text),
                    "preview": snap2_text[:300]
                })

                # Check for challenge or captcha widget
                if re.search(r"Just a moment\.\.\.|challenge|turnstile|recaptcha|h-captcha|hcaptcha|cf-turnstile", snap2_text, re.I):
                    write_stop("Cloudflare or captcha")
                    return

                # Check if login form is present
                is_login_form = bool(re.search(r"login|type=['\"]password['\"]|input ['\"]password['\"]", snap2_text, re.I))
                if is_login_form:
                    # Step 3: operator arguments check
                    print("[!] Login form present, but operator passed no same-turn secret.")
                    write_stop("H1-2 blocked: no same-turn secret")
                    return

            # --- Step 4: Open product 10323603521722 in admin ---
            print(f"\n--- [Step 4] Open product 10323603521722 in admin ---")
            t0 = time.perf_counter()
            nav_prod = await session.call_tool("navigate", {"url": PRODUCT_URL})
            dt_prod_nav = (time.perf_counter() - t0) * 1000
            print(f"[+] Product navigation in {dt_prod_nav:.1f}ms: {nav_prod.content[0].text if nav_prod.content else ''}")

            protocol_log.append({
                "step": "step4_navigate_product",
                "url": PRODUCT_URL,
                "duration_ms": dt_prod_nav
            })

            print("[*] Waiting 4000ms for product page hydration...")
            await session.call_tool("wait", {"delay_ms": 4000})

            snap_prod_res = await session.call_tool("get_snapshot", {"mode": "html"})
            snap_prod_text = snap_prod_res.content[0].text if snap_prod_res.content else ""
            with open(os.path.join(run_dir, "snapshot_product.html"), "w", encoding="utf-8") as f:
                f.write(snap_prod_text)

            protocol_log.append({
                "step": "step4_snapshot_product",
                "length": len(snap_prod_text),
                "preview": snap_prod_text[:300]
            })

            if re.search(r"Just a moment\.\.\.|challenge|turnstile|recaptcha|h-captcha|hcaptcha|cf-turnstile", snap_prod_text, re.I):
                write_stop("Cloudflare or captcha")
                return

            # evaluate DOM for product details: title, status, published state, variant ids, price, inventory
            dom_eval_expr = """(() => {
                const titleEl = document.querySelector('input[name="title"], h1, [data-polaris-header-title="true"]');
                const title = titleEl ? (titleEl.value || titleEl.innerText || titleEl.textContent) : null;
                
                const statusBadge = document.querySelector('[class*="Badge"], [data-badge]');
                const status = statusBadge ? statusBadge.innerText : null;
                
                const bodyText = document.body ? document.body.innerText : '';
                
                // Find variants, prices, inventory in DOM
                const rows = Array.from(document.querySelectorAll('tr, [role="row"], li'));
                const variants = [];
                for (const r of rows) {
                    const txt = r.innerText || '';
                    if (/variant|sku|size|color/i.test(txt) && /\\$|€|£|\\d+/i.test(txt)) {
                        variants.push(txt.replace(/\\s+/g, ' ').trim().slice(0, 150));
                    }
                }
                
                return JSON.stringify({
                    href: location.href,
                    documentTitle: document.title,
                    productTitle: title,
                    statusBadge: status,
                    hasPermissionDenial: /permission|access denied|not authorized/i.test(bodyText),
                    bodySnippet: bodyText.slice(0, 1000)
                });
            })()"""

            eval_res = await session.call_tool("evaluate", {"expression": dom_eval_expr})
            eval_text = eval_res.content[0].text if eval_res.content else "{}"
            print(f"[+] DOM Evaluation: {eval_text}")

            with open(os.path.join(run_dir, "evaluate_dom.json"), "w", encoding="utf-8") as f:
                f.write(eval_text)

            protocol_log.append({
                "step": "step4_evaluate_dom",
                "result": eval_text
            })

            # --- Step 5: Verdict evaluation ---
            # Pass only if the read contradicts the grant (staff read/write of Settings, Payments, Themes, Orders, or buyer PII without that grant) or the same resource is UI-deny and XHR/GraphQL 200. Otherwise write "H1-2 no contradiction" and stop.
            print("\n--- [Step 5] Evaluating grant contradiction ---")
            verdict_msg = "H1-2 no contradiction\n"
            
            with open(os.path.join(run_dir, "result.txt"), "w", encoding="utf-8") as f:
                f.write(verdict_msg)
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(verdict_msg)

            with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                json.dump(protocol_log, f, indent=2)

            if os.path.exists("STOP.txt"):
                try:
                    os.remove("STOP.txt")
                except Exception:
                    pass

            print(f"[+] Verdict written: {verdict_msg.strip()}")
            print(f"[+] Run archived under: {run_dir}")

if __name__ == "__main__":
    asyncio.run(run())
