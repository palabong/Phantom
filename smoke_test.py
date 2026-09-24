import os
import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    token = os.getenv("PHANTOM_AUTH_TOKEN", "ph_live_demo_test")
    url = f"https://phantom-cloud-engine.fly.dev/sse/?token={token}"
    print(f"Connecting to {url}")
    try:
        async with sse_client(url) as streams:
            print("SSE connected.")
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Session initialized.")
                
                tools = await session.list_tools()
                print("Available tools:")
                for t in tools.tools:
                    print(f"- {t.name}")
                
                print("Calling navigate...")
                res = await session.call_tool("navigate", {"url": "https://example.com"})
                print("Navigate result:", res)
                
                print("Calling get_snapshot...")
                res_snap = await session.call_tool("get_snapshot", {"mode": "html"})
                print("Snapshot result length:", len(res_snap.content[0].text))
                print("Snapshot snippet:", res_snap.content[0].text[:200])
                
    except Exception as e:
        print("Error during smoke test:", e)

if __name__ == "__main__":
    asyncio.run(main())
