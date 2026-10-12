import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_D2aZuYtdGL6tUfuV2egoxp"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
STORE_ID = "xxxxxx-r48zg9i1"
PRODUCT_ID = "10323603947706"
TARGET_URL = f"https://admin.shopify.com/store/{STORE_ID}/products/{PRODUCT_ID}"

async def main():
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join("runs", f"prod_postdeploy_{utc_timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    print(f"[*] Archive directory created: {run_dir}")
    print(f"[*] Connecting to {SSE_URL} (one session only)...")

    protocol_log = []

    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] Session initialized.")

            # --- Step 1: get_snapshot html ---
            print("\n--- Step 1: get_snapshot html ---")
            t0 = time.perf_counter()
            snap1_res = await session.call_tool("get_snapshot", {"mode": "html"})
            dt1 = (time.perf_counter() - t0) * 1000
            snap1_text = snap1_res.content[0].text if snap1_res.content else ""
            print(f"[+] Step 1 snapshot received ({len(snap1_text)} chars): {snap1_text[:200]}")

            with open(os.path.join(run_dir, "snapshot_step1.html"), "w", encoding="utf-8") as f:
                f.write(snap1_text)

            protocol_log.append({
                "step": "step1_get_snapshot",
                "duration_ms": dt1,
                "length": len(snap1_text),
                "preview": snap1_text[:200]
            })

            # Check for challenge or captcha
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", snap1_text, re.I):
                print("[!] Challenge or captcha present. Stopping.")
                with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
                    f.write("challenge or captcha present\n")
                with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                    json.dump(protocol_log, f, indent=2)
                return

            # Confirm the current page is an authenticated admin for xxxxxx-r48zg9i1
            # (page title or content references the store products list)
            is_auth_admin = (STORE_ID in snap1_text or "letseewhassup" in snap1_text.lower()) and \
                            ("product" in snap1_text.lower() or "prodotti" in snap1_text.lower())

            if not is_auth_admin:
                print(f"[!] Current page is not an authenticated admin for {STORE_ID}. Stopping.")
                stop_path = os.path.join(run_dir, "STOP.txt")
                with open(stop_path, "w", encoding="utf-8") as f:
                    f.write("authenticated admin session not present\n")
                with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                    json.dump(protocol_log, f, indent=2)
                print(f"[+] STOP.txt written: authenticated admin session not present")
                return

            print(f"[+] Authenticated admin session confirmed for {STORE_ID}.")

            # --- Step 2: navigate once to target product URL ---
            print(f"\n--- Step 2: navigate once to {TARGET_URL} ---")
            t0 = time.perf_counter()
            nav_res = await session.call_tool("navigate", {"url": TARGET_URL})
            dt2 = (time.perf_counter() - t0) * 1000
            nav_text = nav_res.content[0].text if nav_res.content else ""
            print(f"[+] Navigation result: {nav_text}")

            protocol_log.append({
                "step": "step2_navigate",
                "url": TARGET_URL,
                "duration_ms": dt2,
                "result": nav_text
            })

            # Wait for Polaris hydration
            print("[*] Waiting 3000ms for Polaris UI hydration...")
            await session.call_tool("wait", {"delay_ms": 3000})

            # --- Step 3: get_snapshot html ---
            print("\n--- Step 3: get_snapshot html ---")
            t0 = time.perf_counter()
            snap3_res = await session.call_tool("get_snapshot", {"mode": "html"})
            dt3 = (time.perf_counter() - t0) * 1000
            snap3_text = snap3_res.content[0].text if snap3_res.content else ""

            with open(os.path.join(run_dir, "snapshot_product.html"), "w", encoding="utf-8") as f:
                f.write(snap3_text)

            protocol_log.append({
                "step": "step3_get_snapshot",
                "duration_ms": dt3,
                "length": len(snap3_text),
                "preview": snap3_text[:200]
            })

            # Check if challenge or captcha appeared
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", snap3_text, re.I):
                print("[!] Challenge or captcha present after navigate. Stopping.")
                with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
                    f.write("challenge or captcha present\n")
                with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                    json.dump(protocol_log, f, indent=2)
                return

            # Evaluate product fields from DOM
            eval_js = r"""(() => {
                const title = document.title || "";
                const href = location.href || "";
                const bodyText = document.body ? document.body.innerText : "";

                const is404 = /There's no page at this address|404|Page not found/i.test(bodyText);

                // Look for product title input or header
                const titleInput = document.querySelector('input[name="title"], input[id*="title"], [data-product-title]');
                const productTitleVal = titleInput ? (titleInput.value || titleInput.innerText || "") : "";

                // Status
                let statusMatch = bodyText.match(/\b(Active|Draft|Archived)\b/i);
                let status = statusMatch ? statusMatch[0] : null;

                // Inventory
                let invMatch = bodyText.match(/(\d+\s+in\s+stock(?:\s+for\s+\d+\s+variants)?)/i) ||
                               bodyText.match(/(\d+\s+available)/i);
                let inventory = invMatch ? invMatch[0] : null;

                // Price
                let priceMatch = bodyText.match(/\$\d+(\.\d{2})?/);
                let price = priceMatch ? priceMatch[0] : null;

                const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                    name: el.name || el.id || "",
                    value: el.value || "",
                    placeholder: el.placeholder || ""
                })).filter(i => i.value || i.placeholder);

                return JSON.stringify({
                    pageTitle: title,
                    currentUrl: href,
                    is404: is404,
                    productTitle: productTitleVal,
                    status: status,
                    inventory: inventory,
                    price: price,
                    inputsCount: inputs.length,
                    inputs: inputs.slice(0, 20),
                    bodySnippet: bodyText.slice(0, 1000)
                });
            })()"""

            t0 = time.perf_counter()
            eval_res = await session.call_tool("evaluate", {"expression": eval_js})
            dt_eval = (time.perf_counter() - t0) * 1000
            raw_eval = eval_res.content[0].text if eval_res.content else "{}"

            try:
                eval_data = json.loads(raw_eval)
                if isinstance(eval_data, str):
                    eval_data = json.loads(eval_data)
            except Exception:
                eval_data = {"raw": raw_eval}

            with open(os.path.join(run_dir, "evaluate.json"), "w", encoding="utf-8") as f:
                json.dump(eval_data, f, indent=2)

            protocol_log.append({
                "step": "step3_evaluate",
                "duration_ms": dt_eval,
                "data": eval_data
            })

            # --- Step 4 & 5: Check product fields ---
            is_404 = eval_data.get("is404", False)
            has_product_data = bool(eval_data.get("productTitle") or eval_data.get("status") or eval_data.get("inventory") or eval_data.get("price"))

            if is_404 or not has_product_data:
                msg = f"product read complete — no data rendered for {PRODUCT_ID}"
                print(f"[+] {msg}")
                with open(os.path.join(run_dir, "result.txt"), "w", encoding="utf-8") as f:
                    f.write(f"{msg}\n")
            else:
                print(f"[+] Product data present in DOM: title='{eval_data.get('productTitle')}', status='{eval_data.get('status')}', price='{eval_data.get('price')}'")
                with open(os.path.join(run_dir, "result.txt"), "w", encoding="utf-8") as f:
                    f.write(f"Product data captured for {PRODUCT_ID}\n")

            with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                json.dump(protocol_log, f, indent=2)

            print(f"[+] All steps complete. Run archived at {run_dir}")

if __name__ == "__main__":
    asyncio.run(main())
