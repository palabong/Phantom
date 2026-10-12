import os
import sys
import asyncio
import datetime
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_beanie_cart_workflow"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
BASE_URL = "https://xxxxxx-r48zg9i1.myshopify.com"

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to Local Phantom: {SSE_URL}...")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Session initialized.")
            
            tool_call_count = 0
            
            # 1. Navigate directly to: https://xxxxxx-r48zg9i1.myshopify.com/products/beanie.js
            target_product_js = f"{BASE_URL}/products/beanie.js"
            print(f"\n[Tool 1/6] navigate -> {target_product_js}")
            await session.call_tool("navigate", {"url": target_product_js})
            tool_call_count += 1
            
            # 2. Evaluate the page/JSON: Extract price, available, inventory_quantity, variant id
            print(f"\n[Tool 2/6] evaluate -> Extract variant metadata")
            eval_prod = await session.call_tool("evaluate", {"expression": """(() => {
                try {
                    const data = JSON.parse(document.body.innerText);
                    const v0 = (data.variants && data.variants.length > 0) ? data.variants[0] : {};
                    return JSON.stringify({
                        title: data.title,
                        variant_id: v0.id,
                        price: v0.price !== undefined ? (v0.price / 100).toFixed(2) : (data.price ? (data.price / 100).toFixed(2) : null),
                        available: v0.available !== undefined ? v0.available : data.available,
                        inventory_quantity: v0.inventory_quantity !== undefined ? v0.inventory_quantity : (data.inventory_quantity !== undefined ? data.inventory_quantity : null),
                        inventory_management: v0.inventory_management || data.inventory_management || null,
                        raw_variant: v0
                    });
                } catch(e) {
                    return JSON.stringify({ error: String(e), raw_body: document.body ? document.body.innerText.slice(0, 500) : "" });
                }
            })()"""})
            tool_call_count += 1
            
            raw_eval_prod = eval_prod.content[0].text if eval_prod.content else "{}"
            parsed_prod = json.loads(raw_eval_prod)
            if isinstance(parsed_prod, str):
                try:
                    parsed_prod = json.loads(parsed_prod)
                except Exception:
                    pass
            print("Extracted Product Metadata:")
            print(json.dumps(parsed_prod, indent=2))
            
            variant_id = parsed_prod.get("variant_id")
            if not variant_id:
                print(f"Error: Could not extract variant_id: {parsed_prod}")
                return
                
            # 3. Using a single evaluate tool call, execute a fetch request:
            # POST /cart/add.js Payload: {"id": <extracted_variant_id>, "quantity": 999}
            print(f"\n[Tool 3/6] evaluate -> POST /cart/add.js with variant {variant_id} and quantity 999")
            eval_fetch_expr = f"""(() => {{
                try {{
                    fetch('/cart/add.js', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }},
                        body: JSON.stringify({{
                            id: {variant_id},
                            quantity: 999
                        }})
                    }}).then(r => r.json()).then(data => {{
                        window._cart_add_response = data;
                    }}).catch(err => {{
                        window._cart_add_error = String(err);
                    }});
                    
                    // Also try synchronous XHR to catch immediate return
                    try {{
                        const xhr = new XMLHttpRequest();
                        xhr.open('POST', '/cart/add.js', false);
                        xhr.setRequestHeader('Content-Type', 'application/json');
                        xhr.setRequestHeader('Accept', 'application/json');
                        xhr.send(JSON.stringify({{ id: {variant_id}, quantity: 999 }}));
                        return JSON.stringify({{
                            method: 'sync_xhr',
                            status: xhr.status,
                            response: JSON.parse(xhr.responseText)
                        }});
                    }} catch(xhrErr) {{
                        return JSON.stringify({{
                            method: 'fetch_dispatched',
                            xhrError: String(xhrErr)
                        }});
                    }}
                }} catch(e) {{
                    return JSON.stringify({{ error: String(e) }});
                }}
            }})()"""
            
            eval_add = await session.call_tool("evaluate", {"expression": eval_fetch_expr})
            tool_call_count += 1
            raw_eval_add = eval_add.content[0].text if eval_add.content else "{}"
            parsed_add = json.loads(raw_eval_add)
            if isinstance(parsed_add, str):
                try:
                    parsed_add = json.loads(parsed_add)
                except Exception:
                    pass
            print("Cart Add Result:")
            print(json.dumps(parsed_add, indent=2))
            
            # Brief delay for server-side session write
            await asyncio.sleep(1.0)
            
            # 4. Navigate directly to: https://xxxxxx-r48zg9i1.myshopify.com/cart.js
            target_cart_js = f"{BASE_URL}/cart.js"
            print(f"\n[Tool 4/6] navigate -> {target_cart_js}")
            await session.call_tool("navigate", {"url": target_cart_js})
            tool_call_count += 1
            
            # 5. Evaluate the cart JSON: Extract the current quantity of the Beanie line item and explicitly capture any returned errors.
            print(f"\n[Tool 5/6] evaluate -> Extract cart JSON details")
            eval_cart = await session.call_tool("evaluate", {"expression": """(() => {
                try {
                    const data = JSON.parse(document.body.innerText);
                    const items = data.items || [];
                    const beanieItem = items.find(i => 
                        (i.handle && i.handle.toLowerCase().includes('beanie')) ||
                        (i.title && i.title.toLowerCase().includes('beanie')) ||
                        (i.product_title && i.product_title.toLowerCase().includes('beanie'))
                    );
                    
                    return JSON.stringify({
                        status: 'success',
                        item_count: data.item_count,
                        total_price: data.total_price ? (data.total_price / 100).toFixed(2) : null,
                        beanie_item: beanieItem ? {
                            id: beanieItem.id,
                            variant_id: beanieItem.variant_id,
                            title: beanieItem.title,
                            quantity: beanieItem.quantity,
                            price: beanieItem.price ? (beanieItem.price / 100).toFixed(2) : null,
                            line_price: beanieItem.line_price ? (beanieItem.line_price / 100).toFixed(2) : null,
                            discounts: beanieItem.discounts || []
                        } : null,
                        all_items: items.map(i => ({ title: i.title, quantity: i.quantity })),
                        cart_error: data.error || data.description || data.message || null
                    });
                } catch(e) {
                    return JSON.stringify({
                        status: 'parse_error',
                        error: String(e),
                        bodyText: document.body ? document.body.innerText.slice(0, 500) : ''
                    });
                }
            })()"""})
            tool_call_count += 1
            
            raw_eval_cart = eval_cart.content[0].text if eval_cart.content else "{}"
            parsed_cart = json.loads(raw_eval_cart)
            if isinstance(parsed_cart, str):
                try:
                    parsed_cart = json.loads(parsed_cart)
                except Exception:
                    pass
            print("\nCart Evaluation Result:")
            print(json.dumps(parsed_cart, indent=2))
            
            # 6. Write outcome to standard output and run archive
            print(f"\nTotal MCP Tool Calls Used: {tool_call_count} / 6 permitted")
            
            outcome_report = {
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "tool_calls_used": tool_call_count,
                "variant_metadata": {
                    "product": parsed_prod.get("title"),
                    "variant_id": variant_id,
                    "price": parsed_prod.get("price"),
                    "available": parsed_prod.get("available"),
                    "inventory_quantity": parsed_prod.get("inventory_quantity")
                },
                "cart_add_execution": parsed_add,
                "cart_state": parsed_cart
            }
            
            # Save artifact
            out_file = os.path.join(run_dir, "beanie_cart_outcome.json")
            with open(out_file, "w") as f:
                json.dump(outcome_report, f, indent=2)
            print(f"Outcome archived to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
