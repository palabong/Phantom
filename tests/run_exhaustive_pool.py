import asyncio
import time
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8765/sse/?token=ph_live_local_test_001"

async def call(session, tool_name, kwargs, expect_error=False):
    t0 = time.perf_counter()
    res = await session.call_tool(tool_name, kwargs)
    dt = time.perf_counter() - t0
    
    text = res.content[0].text if res.content else ""
    is_error = res.isError or text.startswith("Errore")
    
    status = "FAIL (Unexpected Error)" if is_error and not expect_error else ("PASS (Expected Error)" if is_error and expect_error else "PASS")
    if not is_error and expect_error: status = "FAIL (Expected Error but got success)"
    
    print(f"  [{tool_name.upper()}] {status} ({dt:.2f}s) | Args: {kwargs}")
    if is_error:
        print(f"    -> ErrMsg: {text.strip()[:150]}")
    return text

async def main():
    print(f"Connecting to running Phantom Cloud Server at {SSE_URL} ...")
    
    async with sse_client(SSE_URL, headers={}) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Session Initialized. Starting Exhaustive Pool Tests...\n")
            
            print("=== POOL A: Premature Action Error Handling ===")
            # Assuming browser might be blank or not initialized, but since it's a shared state
            # it might already have a page if we ran a previous test. 
            # We'll just run them and see if they crash the server. If they return graceful errors or succeed, it's fine.
            await call(session, "evaluate", {"expression": "document.title"})
            await call(session, "click", {"x": 10, "y": 10})
            
            print("\n=== POOL B: Standard AX Evasion Flow ===")
            await call(session, "navigate", {"url": "https://bot.sannysoft.com/"})
            await call(session, "wait", {"delay_ms": 500})
            ax_snap = await call(session, "get_snapshot", {"mode": "ax"})
            # Parse a ref to click
            link_match = re.search(r"\[(ax\d+):\s*LINK[^\]]*\]", ax_snap, re.IGNORECASE)
            ref = link_match.group(1) if link_match else "ax1"
            await call(session, "evaluate", {"expression": "document.title"})
            await call(session, "click", {"ref": ref})
            
            print("\n=== POOL C: Cross-Origin Target Swap & Rapid Execution ===")
            # Navigating away should trigger a target swap in Chrome. Our auto-recovery should handle it.
            await call(session, "navigate", {"url": "https://example.com/"})
            # Rapid evaluation to test concurrency/socket stability
            for i in range(3):
                await call(session, "evaluate", {"expression": f"{i} + {i}"})
            
            html_snap = await call(session, "get_snapshot", {"mode": "html"})
            
            print("\n=== POOL D: Coordinate Interactions & Types ===")
            await call(session, "click", {"x": 100, "y": 100})
            await call(session, "evaluate", {"expression": "document.body.innerHTML += '<input id=\"test\" />'"})
            await call(session, "type", {"selector": "#test", "text": "Pool test pass", "clear": True})
            await call(session, "evaluate", {"expression": "document.getElementById('test').value"})

            print("\n=== ALL POOLS EXECUTED ===")

if __name__ == "__main__":
    asyncio.run(main())