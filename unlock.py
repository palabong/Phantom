import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_unlock"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
TARGET_URL = "https://xxxxxx-r48zg9i1.myshopify.com/password"

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
                
                # Navigate to target password page
                print(f"Navigating to {TARGET_URL}...")
                nav_res = await session.call_tool("navigate", {"url": TARGET_URL})
                print("Navigate result:", nav_res.content[0].text if nav_res.content else "")
                await session.call_tool("wait", {"delay_ms": 2000})
                
                print("Getting HTML snapshot of password page...")
                html_res = await session.call_tool("get_snapshot", {"mode": "html"})
                html_text = html_res.content[0].text if html_res.content else ""
                print(f"Snapshot length: {len(html_text)}")
                
                # Find password input ref (default e2)
                pwd_ref = "e2"
                m_pwd = re.search(r"\[(e\d+):\s+INPUT[^\]]*?(?:password|Enter store using password)[^\]]*?\]", html_text, re.I)
                if m_pwd:
                    pwd_ref = m_pwd.group(1)
                
                # Find submit button ref (default e3)
                btn_ref = "e3"
                m_btn = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)[^\]]*?(?:Enter|Submit)[^\]]*?\]", html_text, re.I)
                if m_btn:
                    btn_ref = m_btn.group(1)
                
                print(f"Typing password into {pwd_ref}...")
                await session.call_tool("type", {"ref": pwd_ref, "text": "niablu", "clear": True})
                
                print(f"Clicking submit button {btn_ref}...")
                await session.call_tool("click", {"ref": btn_ref})
                
                print("Waiting 3000ms...")
                await session.call_tool("wait", {"delay_ms": 3000})
                
                print("Getting HTML snapshot after submit...")
                html_res = await session.call_tool("get_snapshot", {"mode": "html"})
                html_text = html_res.content[0].text if html_res.content else ""
                
                print("Evaluating href and title...")
                eval_expr = 'document.location.href + " | " + document.title'
                eval_res = await session.call_tool("evaluate", {"expression": eval_expr})
                eval_text = eval_res.content[0].text if eval_res.content else ""
                print(f"Location: {eval_text}")
                
                if "/password" in eval_text:
                    print("Still on password page. Stuck.")
                    with open(os.path.join(run_dir, "STOP.txt"), "w") as f:
                        f.write("GATE-STUCK")
                    return
                
                print("Unlocked successfully! Scouting storefront...")
                scout_data = {}
                
                # Evaluate home page
                home_eval = 'JSON.stringify([...document.querySelectorAll("a[href*=\'/products/\'], a[href*=\'/collections/\'], .price")].map(el => ({tag:el.tagName, href:el.href||"", text:el.textContent.trim()})))'
                res = await session.call_tool("evaluate", {"expression": home_eval})
                scout_data["home"] = res.content[0].text if res.content else ""
                
                # Navigate to /collections/all
                print("Navigating to /collections/all...")
                await session.call_tool("navigate", {"url": "https://xxxxxx-r48zg9i1.myshopify.com/collections/all"})
                await session.call_tool("wait", {"delay_ms": 2000})
                res = await session.call_tool("evaluate", {"expression": home_eval})
                scout_data["collections_all"] = res.content[0].text if res.content else ""
                
                # Navigate to beanie
                print("Navigating to /products/beanie...")
                await session.call_tool("navigate", {"url": "https://xxxxxx-r48zg9i1.myshopify.com/products/beanie"})
                await session.call_tool("wait", {"delay_ms": 2000})
                p1_eval = 'JSON.stringify({href: document.location.href, title: document.title, price: document.querySelector(".price")?.textContent, available: !document.documentElement.innerHTML.toLowerCase().includes("sold out")})'
                res = await session.call_tool("evaluate", {"expression": p1_eval})
                scout_data["beanie"] = res.content[0].text if res.content else ""
                
                # Navigate to black-sunnies
                print("Navigating to /products/black-sunnies...")
                await session.call_tool("navigate", {"url": "https://xxxxxx-r48zg9i1.myshopify.com/products/black-sunnies"})
                await session.call_tool("wait", {"delay_ms": 2000})
                res = await session.call_tool("evaluate", {"expression": p1_eval})
                scout_data["black-sunnies"] = res.content[0].text if res.content else ""
                
                note_content = "UNLOCKED + storefront scout\n\n"
                for k, v in scout_data.items():
                    note_content += f"--- {k} ---\n{v}\n\n"
                    
                with open(os.path.join(run_dir, "scout_note.txt"), "w") as f:
                    f.write(note_content)
                print(f"Scout complete. Wrote to {run_dir}/scout_note.txt")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
