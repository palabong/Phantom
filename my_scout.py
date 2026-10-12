import os
import sys
import time
import asyncio
import datetime
import json
import traceback
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_test123"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
TARGET_URL = "https://xxxxxx-r48zg9i1.myshopify.com/"

async def main():
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{timestamp}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to {SSE_URL}")
    try:
        async with sse_client(SSE_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Session initialized.")
                
                await session.call_tool("navigate", {"url": TARGET_URL})
                await session.call_tool("wait", {"delay_ms": 2000})
                html_res = await session.call_tool("get_snapshot", {"mode": "html"})
                html_text = html_res.content[0].text if html_res.content else ""
                
                with open(os.path.join(run_dir, "snapshot.html"), "w") as f:
                    f.write(html_text)
                
                eval_expr = "JSON.stringify({href: document.location.href, title: document.title})"
                eval_res = await session.call_tool("evaluate", {"expression": eval_expr})
                eval_text = eval_res.content[0].text if eval_res.content else "{}"
                print(f"Eval result: {eval_text}")
                
                try: 
                    eval_data = json.loads(eval_text)
                    if isinstance(eval_data, str):
                        eval_data = json.loads(eval_data)
                except: 
                    eval_data = {"href": "", "title": ""}
                
                href = eval_data.get("href", "")
                title = eval_data.get("title", "")
                
                if "Just a moment" in title or "challenge" in href.lower() or "captcha" in html_text.lower():
                    with open(os.path.join(run_dir, "STOP.txt"), "w") as f: f.write("Cloudflare or captcha")
                    print("Cloudflare or captcha found.")
                    return

                if "/password" in href or "password" in title.lower() or "store password" in html_text.lower() or "opening soon" in html_text.lower():
                    print("Password gate detected.")
                    
                    auth_match = re.search(r'\[([^\]]+):\s*INPUT\s*\'authenticity_token\'\]', html_text)
                    pwd_match = re.search(r'\[([^\]]+):\s*INPUT\s*\'password\'\]', html_text)
                    btn_match = re.search(r'\[([^\]]+):\s*BUTTON[^\]]*\]', html_text)
                    
                    auth_ref = auth_match.group(1) if auth_match else "None"
                    pwd_ref = pwd_match.group(1) if pwd_match else "None"
                    btn_ref = btn_match.group(1) if btn_match else "None"
                    
                    with open(os.path.join(run_dir, "refs.json"), "w") as f:
                        json.dump({"authenticity_token": auth_ref, "password": pwd_ref, "submit": btn_ref}, f)
                    
                    msg = "GATE: password form present, refs recorded, no unlock this turn"
                    with open(os.path.join(run_dir, "STOP.txt"), "w") as f:
                        f.write(msg)
                    return

                prod_expr = "JSON.stringify(Array.from(document.querySelectorAll('a[href*=\"/products/\"]')).map(el => el.href))"
                prod_res = await session.call_tool("evaluate", {"expression": prod_expr})
                prod_text = prod_res.content[0].text if prod_res.content else "[]"
                
                with open(os.path.join(run_dir, "note.txt"), "w") as f:
                    f.write(f"storefront open, no gate. Products: {prod_text}")

    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
