import asyncio
import websockets
import json
import urllib.request
import datetime
import os

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    # 1. Locate Admin tab
    req = urllib.request.urlopen("http://127.0.0.1:60193/json/list")
    tabs = json.loads(req.read().decode())
    target_tab = None
    for tab in tabs:
        if "admin.shopify.com" in tab.get("url", ""):
            target_tab = tab
            break
            
    if not target_tab:
        print("No active Shopify Admin tab found!")
        return
        
    ws_url = target_tab.get("webSocketDebuggerUrl")
    target_url = "https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/10323603947706"
    print(f"Connecting to tab: {target_tab.get('title')}...")
    
    async with websockets.connect(ws_url) as ws:
        # Enable Page events
        await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
        await ws.recv()
        
        # Navigate to target_url
        print(f"Navigating to {target_url}...")
        await ws.send(json.dumps({
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": target_url}
        }))
        nav_res = json.loads(await ws.recv())
        print(f"Navigation initiated: {nav_res}")
        
        # Wait for page load / network idle
        await asyncio.sleep(5.0)
        
        # Evaluate resulting URL and page title
        await ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "JSON.stringify({href: location.href, title: document.title, bodyText: document.body ? document.body.innerText.slice(0, 1000) : ''})"
            }
        }))
        res_info = json.loads(await ws.recv())
        info = json.loads(res_info.get("result", {}).get("result", {}).get("value", "{}"))
        
        href = info.get("href", "")
        title = info.get("title", "")
        body_text = info.get("bodyText", "")
        
        print("\nResulting Page State:")
        print(f"  URL: {href}")
        print(f"  Title: {title}")
        print(f"  Body Preview:\n{body_text[:400]}")
        
        # Record outcome in run folder
        out_path = os.path.join(run_dir, "navigation_outcome.txt")
        with open(out_path, "w") as f:
            f.write(f"Requested URL: {target_url}\n")
            f.write(f"Final URL: {href}\n")
            f.write(f"Title: {title}\n")
            f.write(f"Body Preview:\n{body_text}\n")
        print(f"\nSaved outcome to {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
