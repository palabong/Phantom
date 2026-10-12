import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession

async def main():
    url = "https://phantom-cloud-engine.fly.dev/sse/?token=D2aZuYtdGL6tUfuV2egoxp"
    async with sse_client(url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            res = await session.call_tool("evaluate", {"expression": "await fetch('/products.json').then(r=>r.status).catch(e=>e.toString())"})
            print(res)

asyncio.run(main())
