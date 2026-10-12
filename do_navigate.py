import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    url = "http://127.0.0.1:8000/sse/?token=D2aZuYtdGL6tUfuV2egoxp"
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Connected successfully!")
                
                result = await session.call_tool("navigate", {"url": "https://xxxxxx-r48zg9i1.myshopify.com/password"})
                print("Navigation result:", result)
                
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
