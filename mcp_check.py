import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    url = "https://phantom-cloud-engine.fly.dev/sse/?token=D2aZuYtdGL6tUfuV2egoxp"
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Connected successfully!")
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                print("Available tools:", ", ".join(tool_names))
                if set(['navigate', 'get_snapshot', 'click', 'type', 'evaluate', 'wait']).issubset(tool_names):
                    print("All six tools are accessible.")
                else:
                    print("Missing some tools.")
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
