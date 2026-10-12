import asyncio
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8000/sse/?token=ph_live_D2aZuYtdGL6tUfuV2egoxp"

async def check():
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            # get_snapshot html
            snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
            snap_text = snap_res.content[0].text if snap_res.content else ""
            
            # evaluate href & title
            eval_res = await session.call_tool("evaluate", {"expression": "JSON.stringify({href: location.href, title: document.title, body: document.body ? document.body.innerText.slice(0, 1000) : ''})"})
            eval_data = json.loads(eval_res.content[0].text) if eval_res.content else {}
            if isinstance(eval_data, str):
                eval_data = json.loads(eval_data)
                
            print("HREF:", eval_data.get("href"))
            print("TITLE:", eval_data.get("title"))
            print("BODY PREVIEW:", eval_data.get("body", "")[:300].replace("\n", " "))
            print("Is funk-it-up in snap?:", "funk-it-up" in snap_text or "funk-it-up" in eval_data.get("href", ""))

asyncio.run(check())
