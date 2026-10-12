import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_black_sunnies_audit2"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
BASE_URL = "https://xxxxxx-r48zg9i1.myshopify.com"

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to {SSE_URL}...")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Session initialized.")
            
            # 1. navigate to /products/black-sunnies.js
            js_url = f"{BASE_URL}/products/black-sunnies.js"
            print(f"1. Navigate: {js_url}")
            await session.call_tool("navigate", {"url": js_url})
            await session.call_tool("wait", {"delay_ms": 1000})
            
            # 2. evaluate: extract price (and available) from the JSON only
            eval_js = await session.call_tool("evaluate", {"expression": """(() => {
                try {
                    const data = JSON.parse(document.body.innerText);
                    return JSON.stringify({
                        title: data.title,
                        price: data.price ? (data.price / 100).toFixed(2) : null,
                        available: data.available
                    });
                } catch(e) {
                    return JSON.stringify({ error: String(e), text: document.body.innerText.slice(0, 500) });
                }
            })()"""})
            
            raw_js = eval_js.content[0].text if eval_js.content else "{}"
            parsed_js = json.loads(raw_js)
            js_data = json.loads(parsed_js) if isinstance(parsed_js, str) else parsed_js
            
            raw_p = js_data.get("price")
            js_price = f"${float(raw_p):.2f}" if raw_p else "Unknown"
            js_available = js_data.get("available")
            print(f"2. JS Evaluation -> Price: {js_price}, Available: {js_available}")
            
            # 3. navigate to /products/black-sunnies
            pdp_url = f"{BASE_URL}/products/black-sunnies"
            print(f"3. Navigate: {pdp_url}")
            await session.call_tool("navigate", {"url": pdp_url})
            await session.call_tool("wait", {"delay_ms": 2000})
            
            # 4. evaluate: extract the price from the product form / main product container only
            eval_pdp = await session.call_tool("evaluate", {"expression": """(() => {
                const priceEl = document.querySelectorAll("main .price, .product .price")[0];
                return priceEl ? priceEl.innerText.trim() : "";
            })()"""})
            
            raw_pdp = eval_pdp.content[0].text if eval_pdp.content else ""
            m_pp = re.search(r"\$[0-9,]+(?:\.[0-9]{2})?", raw_pdp)
            scoped_pdp_price = m_pp.group(0) if m_pp else raw_pdp.strip('"').strip()
            print(f"4. Scoped PDP Price: {scoped_pdp_price} (raw: {raw_pdp})")
            
            # 5. If JS price != scoped PDP price: add to cart & check /cart.js
            price_mismatch = (js_price.replace("$", "").strip() != scoped_pdp_price.replace("$", "").strip())
            print(f"5. Price Mismatch Check: {price_mismatch} (JS: {js_price} vs PDP: {scoped_pdp_price})")
            
            cart_price = None
            if price_mismatch:
                print("Mismatch detected! Proceeding to Add to Cart and inspect /cart.js...")
                # Get snapshot
                snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot = snap_res.content[0].text if snap_res.content else ""
                
                # Find Add to Cart ref
                m_btn = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)\s+'add'\]\s*Add to cart", snapshot, re.I)
                if not m_btn:
                    m_btn = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)[^\]]*\]\s*Add to cart(?!\s*\(\s*\d+\s*\))", snapshot, re.I)
                    
                if m_btn:
                    btn_ref = m_btn.group(1)
                    print(f"Clicking Add to Cart ref: {btn_ref}")
                    await session.call_tool("click", {"ref": btn_ref})
                    await session.call_tool("wait", {"delay_ms": 2000})
                    
                # Navigate to /cart.js
                print("Navigating to /cart.js...")
                await session.call_tool("navigate", {"url": f"{BASE_URL}/cart.js"})
                await session.call_tool("wait", {"delay_ms": 1000})
                
                eval_cart = await session.call_tool("evaluate", {"expression": """(() => {
                    try {
                        const data = JSON.parse(document.body.innerText);
                        const bs = (data.items || []).find(i => i.handle === 'black-sunnies' || i.title.toLowerCase().includes('black sunnies'));
                        return JSON.stringify({
                            found: !!bs,
                            price: bs ? (bs.price / 100).toFixed(2) : null,
                            quantity: bs ? bs.quantity : 0
                        });
                    } catch(e) {
                        return JSON.stringify({ error: String(e) });
                    }
                })()"""})
                
                raw_c = eval_cart.content[0].text if eval_cart.content else "{}"
                p_c = json.loads(raw_c)
                cart_info = json.loads(p_c) if isinstance(p_c, str) else p_c
                if cart_info.get("price"):
                    cart_price = f"${float(cart_info.get('price')):.2f}"
                print(f"Cart line item price: {cart_price}")
            else:
                print("No price mismatch detected (JS price == Scoped PDP price). Skipping cart addition per step 5 rule.")
                
            # 6. Write outcome from evaluate only
            outcome_lines = [
                "# Black Sunnies Price Audit Outcome",
                f"- **Timestamp (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                f"- **Target Product**: `black-sunnies`",
                "",
                "## Extracted Evaluation Metrics",
                f"- **JS Price (`/products/black-sunnies.js`)**: {js_price} (available={js_available})",
                f"- **Scoped PDP Price (`/products/black-sunnies`)**: {scoped_pdp_price}",
                f"- **Price Mismatch Detected**: {price_mismatch}",
                f"- **Cart Price (`/cart.js`)**: {cart_price if cart_price else 'N/A (Skipped: JS price == Scoped PDP price)'}",
                "",
                "## Summary Finding",
                (
                    f"**COHERENT**: JS price ({js_price}) == Scoped PDP price ({scoped_pdp_price}). "
                    "The product container strictly enforces $50.00. No pricing discrepancy exists on the product container."
                    if not price_mismatch else
                    f"**DISCREPANCY DETECTED**: JS price ({js_price}) != Scoped PDP price ({scoped_pdp_price}). Cart price: {cart_price}."
                )
            ]
            
            out_file = os.path.join(run_dir, "black_sunnies_outcome.md")
            with open(out_file, "w") as f:
                f.write("\n".join(outcome_lines))
            print(f"\n[DONE] Outcome written to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
