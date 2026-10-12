import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_beanie_audit"
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
            
            # 1. navigate to /products/beanie.js
            js_url = f"{BASE_URL}/products/beanie.js"
            print(f"1. Navigate: {js_url}")
            await session.call_tool("navigate", {"url": js_url})
            await session.call_tool("wait", {"delay_ms": 1000})
            
            # 2. evaluate: extract price, available, and any inventory_quantity if present
            eval_js = await session.call_tool("evaluate", {"expression": """(() => {
                try {
                    const data = JSON.parse(document.body.innerText);
                    const v0 = (data.variants && data.variants.length > 0) ? data.variants[0] : {};
                    return JSON.stringify({
                        title: data.title,
                        price: data.price ? (data.price / 100).toFixed(2) : null,
                        available: data.available,
                        first_variant_id: v0.id,
                        first_variant_price: v0.price ? (v0.price / 100).toFixed(2) : null,
                        first_variant_available: v0.available,
                        inventory_quantity: v0.inventory_quantity !== undefined ? v0.inventory_quantity : data.inventory_quantity,
                        inventory_management: v0.inventory_management !== undefined ? v0.inventory_management : data.inventory_management,
                        raw_variant: v0
                    });
                } catch(e) {
                    return JSON.stringify({ error: String(e), text: document.body.innerText.slice(0, 500) });
                }
            })()"""})
            
            raw_js = eval_js.content[0].text if eval_js.content else "{}"
            parsed_js = json.loads(raw_js)
            js_data = json.loads(parsed_js) if isinstance(parsed_js, str) else parsed_js
            print("2. JS Metadata:", json.dumps(js_data, indent=2))
            
            variant_id = js_data.get("first_variant_id")
            
            # 3. One evaluate fetch POST /cart/add.js with {id: <variant>, quantity: 999}
            print(f"3. Calling POST /cart/add.js with variant {variant_id} and quantity 999...")
            # We first navigate to home or product page so fetch is same-origin
            await session.call_tool("navigate", {"url": f"{BASE_URL}/products/beanie"})
            await session.call_tool("wait", {"delay_ms": 1000})
            
            eval_add = await session.call_tool("evaluate", {"expression": f"""(async () => {{
                try {{
                    const resp = await fetch('/cart/add.js', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }},
                        body: JSON.stringify({{
                            id: {variant_id},
                            quantity: 999
                        }})
                    }});
                    const data = await resp.json();
                    return JSON.stringify({{
                        status: resp.status,
                        ok: resp.ok,
                        data: data
                    }});
                }} catch (e) {{
                    return JSON.stringify({{ error: String(e) }});
                }}
            }})()"""})
            
            raw_add = eval_add.content[0].text if eval_add.content else "{}"
            add_result = json.loads(raw_add) if raw_add != "null" else None
            if isinstance(add_result, str):
                try:
                    add_result = json.loads(add_result)
                except Exception:
                    pass
            print("3. Cart Add Response:", add_result)
            
            # Wait 1000ms
            await session.call_tool("wait", {"delay_ms": 1500})
            
            # 4. navigate to /cart.js
            print(f"4. Navigate: {BASE_URL}/cart.js")
            await session.call_tool("navigate", {"url": f"{BASE_URL}/cart.js"})
            await session.call_tool("wait", {"delay_ms": 1000})
            
            # 5. evaluate: extract the beanie line item quantity and any error
            eval_cart = await session.call_tool("evaluate", {"expression": """(() => {
                try {
                    const data = JSON.parse(document.body.innerText);
                    const beanie = (data.items || []).find(i => i.handle === 'beanie' || i.title.toLowerCase().includes('beanie'));
                    return JSON.stringify({
                        item_count: data.item_count,
                        beanie_line_item: beanie ? {
                            id: beanie.id,
                            title: beanie.title,
                            quantity: beanie.quantity,
                            price: (beanie.price / 100).toFixed(2),
                            line_price: (beanie.line_price / 100).toFixed(2)
                        } : null,
                        error: data.error || data.description || null
                    });
                } catch(e) {
                    return JSON.stringify({ error: String(e), text: document.body.innerText.slice(0, 500) });
                }
            })()"""})
            
            raw_cart = eval_cart.content[0].text if eval_cart.content else "{}"
            parsed_cart = json.loads(raw_cart)
            cart_info = json.loads(parsed_cart) if isinstance(parsed_cart, str) else parsed_cart
            print("5. Cart Status:", json.dumps(cart_info, indent=2))
            
            # 6. Write outcome from evaluate only
            beanie_item = cart_info.get("beanie_line_item")
            beanie_qty = beanie_item.get("quantity") if beanie_item else 0
            
            outcome_lines = [
                "# Beanie Inventory & Cart Quantity Evaluation",
                f"- **Timestamp (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                f"- **Target**: `https://xxxxxx-r48zg9i1.myshopify.com`",
                "",
                "## 1. Product JS Evaluation (`/products/beanie.js`)",
                f"- **Title**: {js_data.get('title')}",
                f"- **Price**: ${js_data.get('price')}",
                f"- **Available**: {js_data.get('available')}",
                f"- **First Variant ID**: {variant_id}",
                f"- **Inventory Quantity**: {js_data.get('inventory_quantity') if js_data.get('inventory_quantity') is not None else 'Not exposed in public JS endpoint'}",
                f"- **Inventory Management**: {js_data.get('inventory_management') if js_data.get('inventory_management') is not None else 'Not exposed in public JS endpoint'}",
                "",
                "## 2. Cart Add Request (`POST /cart/add.js`)",
                f"- **Requested Payload**: `{{ id: {variant_id}, quantity: 999 }}`",
                f"- **Server Response**: {json.dumps(add_result)}",
                "",
                "## 3. Cart State Evaluation (`/cart.js`)",
                f"- **Total Cart Items**: {cart_info.get('item_count')}",
                f"- **Beanie Line Item**: {json.dumps(beanie_item)}",
                f"- **Beanie Quantity in Cart**: {beanie_qty}",
                f"- **Quantity Handling**: {'Accepted 999 units' if beanie_qty >= 999 else f'Capped / Restricted to {beanie_qty} units' if beanie_qty > 0 else 'Rejected addition'}",
                f"- **Error Message**: {cart_info.get('error') or (add_result.get('data', {}).get('description') if add_result and isinstance(add_result.get('data'), dict) else 'None')}"
            ]
            
            out_file = os.path.join(run_dir, "beanie_quantity_outcome.md")
            with open(out_file, "w") as f:
                f.write("\n".join(outcome_lines))
            print(f"\n[DONE] Outcome written to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
