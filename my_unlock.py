import os
import sys
import datetime
import asyncio
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_test123"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"

async def main():
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{timestamp}"
    os.makedirs(run_dir, exist_ok=True)
    
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            # 1. type
            await session.call_tool("type", {"ref": "e2", "text": "niablu", "clear": True})
            
            # 2. click
            await session.call_tool("click", {"ref": "e3"})
            
            # 3. wait
            await session.call_tool("wait", {"delay_ms": 3000})
            
            # 4. get_snapshot mode=html
            await session.call_tool("get_snapshot", {"mode": "html"})
            
            # 5. evaluate href and title
            eval_expr = "JSON.stringify({href: document.location.href, title: document.title})"
            res = await session.call_tool("evaluate", {"expression": eval_expr})
            eval_data = json.loads(res.content[0].text) if res.content else {}
            if isinstance(eval_data, str):
                eval_data = json.loads(eval_data)
            
            href = eval_data.get("href", "")
            
            # 6. If href still contains /password
            if "/password" in href:
                with open(os.path.join(run_dir, "STOP.txt"), "w") as f:
                    f.write("GATE-STUCK")
                return
            
            # 7. If storefront loads
            prod_expr = """
            JSON.stringify(Array.from(document.querySelectorAll('a[href*="/products/"]')).map(el => {
                let priceEl = document.querySelector('.price');
                return {
                    href: el.href,
                    price: priceEl ? priceEl.textContent.trim() : null,
                    available: !document.documentElement.innerHTML.toLowerCase().includes('sold out')
                };
            }))
            """
            prod_res = await session.call_tool("evaluate", {"expression": prod_expr})
            prod_text = prod_res.content[0].text if prod_res.content else "[]"
            
            with open(os.path.join(run_dir, "note.txt"), "w") as f:
                f.write(f"UNLOCKED {href}\nProducts: {prod_text}")

if __name__ == "__main__":
    asyncio.run(main())
