import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession

async def main():
    url = "http://127.0.0.1:8000/sse/?token=ph_live_test_beanie"
    print(f"Connecting to {url}...")
    async with sse_client(url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Session initialized. Calling navigate...")
            res = await session.call_tool("navigate", {"url": "https://xxxxxx-r48zg9i1.myshopify.com/products/beanie.js"})
            print("Navigate result:", res)

if __name__ == "__main__":
    asyncio.run(main())
