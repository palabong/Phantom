import asyncio
import websockets
import json
import glob
import os

async def main():
    run_dirs = sorted(glob.glob("runs/prod_postdeploy_*"))
    latest_dir = run_dirs[-1] if run_dirs else "runs"
    
    ws_url = "ws://127.0.0.1:60193/devtools/page/AD695A1550D3BCFD051F92DCED6F53D3"
    print(f"Connecting to {ws_url}...")
    
    async with websockets.connect(ws_url) as ws:
        msg_id = 100
        req = {
            "id": msg_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """(() => {
                    const title = document.title;
                    const href = location.href;
                    const bodyText = document.body ? document.body.innerText : "";
                    
                    // Look for banner / error / not found messages
                    const banners = Array.from(document.querySelectorAll('[role="alert"], [role="status"], .Polaris-Banner, .Polaris-ExceptionList, h1, h2, p')).map(e => e.innerText.trim()).filter(Boolean);
                    
                    return JSON.stringify({
                        title: title,
                        href: href,
                        banners: banners.slice(0, 20),
                        bodyPreview: bodyText.slice(0, 1500),
                        isNotFound: bodyText.toLowerCase().includes("not found") || bodyText.toLowerCase().includes("could not be found") || bodyText.toLowerCase().includes("doesn't exist") || bodyText.toLowerCase().includes("non trovato")
                    });
                })()"""
            }
        }
        await ws.send(json.dumps(req))
        
        while True:
            resp = json.loads(await ws.recv())
            if resp.get("id") == msg_id:
                val = resp.get("result", {}).get("result", {}).get("value", "{}")
                data = json.loads(val)
                print("\n=== Result on target page ===")
                print(f"URL: {data.get('href')}")
                print(f"Title: {data.get('title')}")
                print(f"isNotFound: {data.get('isNotFound')}")
                print(f"Banners / Headers:\n{json.dumps(data.get('banners'), indent=2)}")
                print(f"\nBody Preview:\n{data.get('bodyPreview')}")
                
                # Save outcome file
                out_path = os.path.join(latest_dir, "navigation_outcome.txt")
                with open(out_path, "w") as f:
                    f.write(f"Final URL: {data.get('href')}\n")
                    f.write(f"Title: {data.get('title')}\n")
                    f.write(f"isNotFound: {data.get('isNotFound')}\n\n")
                    f.write(f"Banners:\n{json.dumps(data.get('banners'), indent=2)}\n\n")
                    f.write(f"Body text:\n{data.get('bodyPreview')}\n")
                print(f"\nWrote outcome to {out_path}")
                break

if __name__ == "__main__":
    asyncio.run(main())
