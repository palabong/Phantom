import asyncio
import time
from mcp.client.sse import sse_client
from mcp import ClientSession
import mcp.types as types

SSE_URL = "http://127.0.0.1:8765/sse/?token=ph_live_local_test_001"
TARGET_URL = "https://bot.sannysoft.com/"

async def call(session, tool_name, kwargs):
    print(f"\n[EXEC] Tool: {tool_name} | Args: {kwargs}")
    t0 = time.perf_counter()
    try:
        res = await session.call_tool(tool_name, kwargs)
        dt = time.perf_counter() - t0
        text = res.content[0].text if res.content else ""
        is_error = res.isError or text.startswith("Errore")
        status = "ERROR" if is_error else "SUCCESS"
        print(f"  -> {status} | Latency: {dt*1000:.1f}ms | Payload Length: {len(text)}")
        if is_error:
            print(f"  -> Msg: {text}")
        return text
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"  -> EXCEPTION | Latency: {dt*1000:.1f}ms | {type(e).__name__}: {str(e)}")
        return None

async def main():
    print(f"Connecting to live MCP Server at {SSE_URL} ...")
    async with sse_client(SSE_URL, headers={}) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Session established. Commencing Test Matrix...\n")
            
            print("==========================================================")
            print(" PATTERN A (State Ingestion & Discovery)")
            print("==========================================================")
            # navigate is native. No timeout parameter natively, but we pass URL.
            await call(session, "navigate", {"url": TARGET_URL})
            # get_snapshot natively accepts 'mode' (html/ax). Max_chars isn't a native arg, but we will pass mode="html"
            snap1 = await call(session, "get_snapshot", {"mode": "html"})
            if snap1:
                print(f"  -> Truncated snippet: {snap1[:100]}...")
                
            print("\n==========================================================")
            print(" PATTERN B (Viewport Manipulation & Visual Telemetry)")
            print("==========================================================")
            # scroll is not native, we emulate via evaluate
            print("  [Adapter] 'scroll' not in schema. Emulating via 'evaluate'...")
            await call(session, "evaluate", {"expression": "window.scrollBy(0, 600); 'scrolled_down'"})
            
            # take_screenshot is not native. We invoke it directly to test strict protocol errors.
            print("  [Adapter] Invoking unregistered tool 'take_screenshot' to test conformance...")
            await call(session, "take_screenshot", {"full_page": False})
            
            print("\n==========================================================")
            print(" PATTERN C (Targeted Interaction & Synchronization)")
            print("==========================================================")
            # wait_for with text is not native. We will use evaluate to poll/check for the text presence.
            print("  [Adapter] 'wait_for' not natively checking text. Emulating check via 'evaluate'...")
            js_check = "Array.from(document.querySelectorAll('th, td')).some(el => el.textContent.includes('Broken Image Dimensions'))"
            await call(session, "evaluate", {"expression": js_check})
            
            # click using e1 (HTML AOM mode ref)
            await call(session, "click", {"ref": "e1"})
            
            print("\n==========================================================")
            print(" PATTERN D (State Modification & Full Recovery)")
            print("==========================================================")
            # scroll to top
            print("  [Adapter] Emulating scroll to top via 'evaluate'...")
            await call(session, "evaluate", {"expression": "window.scrollTo(0, 0); 'scrolled_top'"})
            
            # Final snapshot
            snap2 = await call(session, "get_snapshot", {"mode": "html"})
            if snap2:
                print(f"  -> Final Payload Verification Length: {len(snap2)} chars.")
                
            print("\nMatrix Evaluation Complete.")

if __name__ == "__main__":
    asyncio.run(main())