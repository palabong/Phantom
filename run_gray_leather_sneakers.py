import asyncio
import websockets
import json
import urllib.request
import datetime
import os
import re
from html.parser import HTMLParser

class AOMDistiller(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ignore_block = False
        self.text_buffer = []
        self.elements = {}
        self.e_counter = 1
        
    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "svg", "meta", "noscript", "canvas", "link"]:
            self.in_ignore_block = True
            return
        attr_dict = dict(attrs)
        tag_upper = tag.upper()
        name = attr_dict.get("name") or attr_dict.get("placeholder") or attr_dict.get("aria-label") or attr_dict.get("id") or "unnamed"
        ref_id = f"e{self.e_counter}"
        self.e_counter += 1
        self.elements[ref_id] = {
            "tag": tag_upper,
            "name": name,
            "attrs": attr_dict,
            "id": attr_dict.get("id", ""),
            "class": attr_dict.get("class", "")
        }
        self.text_buffer.append(f"[{ref_id}: {tag_upper} '{name}']")
        
    def handle_endtag(self, tag):
        if tag in ["script", "style", "svg", "meta", "noscript", "canvas", "link"]:
            self.in_ignore_block = False
            
    def handle_data(self, data):
        if not self.in_ignore_block:
            cleaned = data.strip()
            if cleaned:
                self.text_buffer.append(cleaned)

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 1
        
    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("DOM.enable")
        
    async def close(self):
        if self.ws:
            await self.ws.close()
            
    async def send(self, method, params=None):
        mid = self.msg_id
        self.msg_id += 1
        payload = {"id": mid, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        while True:
            raw = await self.ws.recv()
            resp = json.loads(raw)
            if resp.get("id") == mid:
                return resp
                
    async def navigate(self, url):
        print(f"Navigating to {url}...")
        await self.send("Page.navigate", {"url": url})
        # Wait for page lifecycle
        await asyncio.sleep(3.0)
        
    async def evaluate(self, expression):
        res = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        val = res.get("result", {}).get("result", {}).get("value")
        return val

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    # 1. Connect to active Chrome tab
    req = urllib.request.urlopen("http://127.0.0.1:60193/json/list")
    tabs = json.loads(req.read().decode())
    target_tab = None
    for tab in tabs:
        if "admin.shopify.com" in tab.get("url", "") or "myshopify.com" in tab.get("url", ""):
            target_tab = tab
            break
    if not target_tab:
        target_tab = tabs[0]
        
    client = CDPClient(target_tab["webSocketDebuggerUrl"])
    await client.connect()
    print("Connected to CDP tab.")
    
    # --- Step 1: navigate to /products/gray-leather-sneakers.js ---
    js_url = "https://xxxxxx-r48zg9i1.myshopify.com/products/gray-leather-sneakers.js"
    await client.navigate(js_url)
    
    # --- Step 2: evaluate: extract price and available ---
    eval_js_res = await client.evaluate("""(() => {
        try {
            const data = JSON.parse(document.body.innerText);
            return {
                title: data.title,
                price_cents: data.price,
                price_formatted: (data.price / 100).toFixed(2),
                available: data.available,
                variants_count: data.variants ? data.variants.length : 0
            };
        } catch(e) {
            return { error: String(e), text: document.body.innerText.slice(0, 500) };
        }
    })()""")
    print(f"Step 2 Evaluate JS: {eval_js_res}")
    js_price = f"${float(eval_js_res.get('price_formatted', 0)):.2f}"
    js_available = eval_js_res.get("available")
    
    # --- Step 3: navigate to /products/gray-leather-sneakers ---
    pdp_url = "https://xxxxxx-r48zg9i1.myshopify.com/products/gray-leather-sneakers"
    await client.navigate(pdp_url)
    await asyncio.sleep(2.0)
    
    # --- Step 4: Snapshot and One click on Add to cart button ---
    html_content = await client.evaluate("document.documentElement.outerHTML")
    distiller = AOMDistiller()
    distiller.feed(html_content)
    snapshot = " ".join(distiller.text_buffer)
    print(f"Snapshot length: {len(snapshot)} chars")
    
    # Click the Add to cart button via selector / evaluate
    click_res = await client.evaluate("""(() => {
        // Find Add to Cart button in product form
        let btn = document.querySelector('form[action*="/cart/add"] button[name="add"], button[name="add"], .product-form__submit');
        if (!btn) {
            btn = Array.from(document.querySelectorAll('button, input[type="submit"]')).find(b => /add to cart/i.test(b.innerText || b.value));
        }
        if (btn) {
            btn.scrollIntoView({ behavior: 'instant', block: 'center' });
            btn.click();
            return { clicked: true, tag: btn.tagName, name: btn.name, text: btn.innerText.trim() };
        }
        return { clicked: false, error: "Button not found" };
    })()""")
    print(f"Step 4 Click result: {click_res}")
    print("Waiting 2000ms after click...")
    await asyncio.sleep(2.5)
    
    # --- Step 5: navigate to /cart.js ---
    cart_js_url = "https://xxxxxx-r48zg9i1.myshopify.com/cart.js"
    await client.navigate(cart_js_url)
    
    # --- Step 6: evaluate: extract line item price. Compare to JS price ---
    cart_data = await client.evaluate("""(() => {
        try {
            const data = JSON.parse(document.body.innerText);
            return {
                item_count: data.item_count,
                total_price: (data.total_price / 100).toFixed(2),
                items: (data.items || []).map(i => ({
                    id: i.id,
                    handle: i.handle,
                    title: i.title,
                    price: (i.price / 100).toFixed(2),
                    line_price: (i.line_price / 100).toFixed(2),
                    quantity: i.quantity
                }))
            };
        } catch(e) {
            return { error: String(e), text: document.body.innerText.slice(0, 500) };
        }
    })()""")
    print(f"Step 6 Cart.js Data:\n{json.dumps(cart_data, indent=2)}")
    
    # Find gray-leather-sneakers line item in cart
    matching_item = None
    cart_item_price = None
    for item in cart_data.get("items", []):
        if "gray-leather-sneakers" in item.get("handle", "") or "gray leather" in item.get("title", "").lower():
            matching_item = item
            cart_item_price = f"${float(item.get('price', 0)):.2f}"
            break
            
    # Comparison
    comparison_match = (js_price == cart_item_price)
    print(f"\nPrice Comparison:")
    print(f"  Product JS Price: {js_price}")
    print(f"  Cart Line Item Price: {cart_item_price}")
    print(f"  Matches: {comparison_match}")
    
    # --- Step 7: Write outcome from evaluate only ---
    outcome_lines = [
        "# Gray Leather Sneakers Evaluation Outcome",
        f"- **Timestamp (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
        f"- **Product Handle**: `gray-leather-sneakers`",
        "",
        "## 1. Product JS Evaluation (`/products/gray-leather-sneakers.js`)",
        f"- **Title**: {eval_js_res.get('title')}",
        f"- **Price**: {js_price}",
        f"- **Available**: {js_available}",
        f"- **Variants Count**: {eval_js_res.get('variants_count')}",
        "",
        "## 2. Cart Add Action (`/products/gray-leather-sneakers`)",
        f"- **Click Execution**: {json.dumps(click_res)}",
        "",
        "## 3. Cart State Evaluation (`/cart.js`)",
        f"- **Total Items in Cart**: {cart_data.get('item_count')}",
        f"- **Cart Total Price**: ${cart_data.get('total_price')}",
        f"- **Matching Line Item**: {json.dumps(matching_item)}",
        f"- **Cart Line Item Price**: {cart_item_price}",
        "",
        "## 4. Price Comparison & Conclusion",
        f"- **Product JS Price**: {js_price}",
        f"- **Cart Line Item Price**: {cart_item_price}",
        f"- **Coherence Check**: {'MATCH (No price discrepancy)' if comparison_match else 'MISMATCH (Contradiction detected)'}",
        "",
        "## Full Cart Items JSON",
        "```json",
        json.dumps(cart_data, indent=2),
        "```"
    ]
    
    out_file = os.path.join(run_dir, "gray_leather_sneakers_outcome.md")
    with open(out_file, "w") as f:
        f.write("\n".join(outcome_lines))
    print(f"\n[DONE] Outcome written to {out_file}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
