import asyncio
import websockets
import json
import datetime
import os
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
        self.elements[ref_id] = {"tag": tag_upper, "context": name, "selector": f"[data-phantom-ref=\"{ref_id}\"]"}
        self.text_buffer.append(f"[{ref_id}: {tag_upper} '{name}']")
        
    def handle_endtag(self, tag):
        if tag in ["script", "style", "svg", "meta", "noscript", "canvas", "link"]:
            self.in_ignore_block = False
            
    def handle_data(self, data):
        if not self.in_ignore_block:
            cleaned = data.strip()
            if cleaned:
                self.text_buffer.append(cleaned)

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    # Query Chrome debugging targets
    import urllib.request
    req = urllib.request.urlopen("http://127.0.0.1:60193/json/list")
    tabs = json.loads(req.read().decode())
    
    # Find the active shopify tab
    target_tab = None
    for tab in tabs:
        if "admin.shopify.com" in tab.get("url", "") or "myshopify.com" in tab.get("url", ""):
            target_tab = tab
            break
            
    if not target_tab:
        target_tab = tabs[0]
        
    print(f"Inspecting tab: {target_tab.get('title')} ({target_tab.get('url')})")
    ws_url = target_tab.get("webSocketDebuggerUrl")
    
    async with websockets.connect(ws_url) as ws:
        # 1. Evaluate page info
        await ws.send(json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "JSON.stringify({href: location.href, title: document.title, text: document.body ? document.body.innerText.slice(0, 2000) : ''})"
            }
        }))
        res = json.loads(await ws.recv())
        val = res.get("result", {}).get("result", {}).get("value", "{}")
        info = json.loads(val)
        
        href = info.get("href", "")
        title = info.get("title", "")
        text = info.get("text", "")
        
        # 2. Get HTML for snapshot
        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": "document.documentElement.outerHTML"}
        }))
        res_html = json.loads(await ws.recv())
        html = res_html.get("result", {}).get("result", {}).get("value", "")
        
        distiller = AOMDistiller()
        distiller.feed(html)
        snapshot = " ".join(distiller.text_buffer)
        
        print(f"\nPage Evaluation:")
        print(f"  URL: {href}")
        print(f"  Title: {title}")
        print(f"  Snapshot length: {len(snapshot)} chars")
        print(f"  Body excerpt: {text[:200]}...")
        
        # Check conditions
        is_challenge = any(k in href.lower() or k in title.lower() or k in snapshot.lower() for k in [
            "challenge", "turnstile", "hcaptcha", "recaptcha", "just a moment..."
        ])
        is_login = any(k in href.lower() or k in snapshot.lower() for k in [
            "accounts.shopify.com/login", "password"
        ]) and "admin.shopify.com" not in href
        
        is_admin = "admin.shopify.com/store/xxxxxx-r48zg9i1" in href or "xxxxxx-r48zg9i1.myshopify.com/admin" in href
        is_storefront = "xxxxxx-r48zg9i1.myshopify.com" in href
        
        print(f"\nCondition Checks:")
        print(f"  is_challenge: {is_challenge}")
        print(f"  is_login: {is_login}")
        print(f"  is_admin: {is_admin}")
        print(f"  is_storefront: {is_storefront}")
        
        if is_challenge or (not is_admin and not is_storefront):
            stop_path = os.path.join(run_dir, "STOP.txt")
            with open(stop_path, "w") as f:
                f.write("challenge or not authenticated\n")
            print(f"\n[STOP] Wrote {stop_path}: challenge or not authenticated")
        else:
            state_desc = "authenticated admin of xxxxxx-r48zg9i1" if is_admin else "storefront of xxxxxx-r48zg9i1"
            print(f"\n[CONFIRMED] Active session state: {state_desc}")
            
        # Save snapshot artifact
        snap_path = os.path.join(run_dir, "snapshot.txt")
        with open(snap_path, "w") as f:
            f.write(f"URL: {href}\nTitle: {title}\n\nSnapshot:\n{snapshot}")
        print(f"Saved snapshot to {snap_path}")

if __name__ == "__main__":
    asyncio.run(main())
