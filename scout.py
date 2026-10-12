import os
import sys
import time
import asyncio
import datetime
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "D2aZuYtdGL6tUfuV2egoxp"
SSE_URL = f"https://phantom-cloud-engine.fly.dev/sse/?token={TOKEN}"
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
                
                # 1. navigate
                print(f"Navigating to {TARGET_URL}")
                await session.call_tool("navigate", {"url": TARGET_URL})
                
                # 2. wait 2000
                print("Waiting 2000ms")
                await session.call_tool("wait", {"delay_ms": 2000})
                
                # 3. get_snapshot mode=html
                print("Getting HTML snapshot")
                html_res = await session.call_tool("get_snapshot", {"mode": "html"})
                html_text = html_res.content[0].text if html_res.content else ""
                
                with open(os.path.join(run_dir, "snapshot.html"), "w") as f:
                    f.write(html_text)
                print("Saved snapshot.html")
                
                # 4. evaluate href and title
                eval_expr = "JSON.stringify({href: document.location.href, title: document.title})"
                print("Evaluating href and title")
                eval_res = await session.call_tool("evaluate", {"expression": eval_expr})
                eval_text = eval_res.content[0].text if eval_res.content else "{}"
                print(f"Eval result: {eval_text}")
                
                with open(os.path.join(run_dir, "eval.json"), "w") as f:
                    f.write(eval_text)
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
