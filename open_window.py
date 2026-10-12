import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    url = "https://phantom-cloud-engine.fly.dev/sse/?token=D2aZuYtdGL6tUfuV2egoxp"
    async with sse_client(url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Connected to phantom-cloud-engine MCP")
            res = await session.call_tool("navigate", {"url": "about:blank"})
            print(res.content[0].text)

asyncio.run(main())
