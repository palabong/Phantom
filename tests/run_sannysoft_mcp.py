import asyncio
import time
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8765/sse/?token=ph_live_local_test_001"
TARGET_URL = "https://bot.sannysoft.com/"

async def main():
    print(f"Connecting to running Phantom Cloud Server at {SSE_URL} ...")
    
    async with sse_client(SSE_URL, headers={}) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Session Initialized!")
            
            # 1. List Tools
            tools_res = await session.list_tools()
            print(f"Tools Registered: {[t.name for t in tools_res.tools]}")
            
            # 2. Navigate
            print(f"\n-> Navigating to {TARGET_URL} ...")
            t0 = time.perf_counter()
            nav_res = await session.call_tool("navigate", {"url": TARGET_URL})
            print(f"Navigate Response ({time.perf_counter()-t0:.2f}s): {nav_res.content[0].text.strip()}")
            
            # 3. Get AX Snapshot
            print("\n-> Fetching AX Snapshot ...")
            t0 = time.perf_counter()
            snap_res = await session.call_tool("get_snapshot", {"mode": "ax"})
            snap_text = snap_res.content[0].text
            print(f"Snapshot received ({time.perf_counter()-t0:.2f}s), len: {len(snap_text)}")
            print("Snapshot Preview (First 200 chars):")
            print(snap_text[:200] + "...\n")
            
            # Dynamically parse AX tree for a link and a checkbox or table row to test interactions
            print("Parsing AX tree for interactive elements...")
            # We'll look for the "Fingerprint Scanner" link on sannysoft
            link_match = re.search(r"\[(ax\d+):\s*LINK\s+'Fingerprint Scanner'\]", snap_text, re.IGNORECASE)
            link_ref = link_match.group(1) if link_match else "ax26"
            print(f"Found link ref: {link_ref}")
            
            # 4. Evaluate (Pre-click check)
            print("\n-> Evaluating document title...")
            eval_res1 = await session.call_tool("evaluate", {"expression": "document.title"})
            print(f"Current Title: {eval_res1.content[0].text.strip()}")
            
            # 5. Type (Though Sannysoft has no obvious input we need to type into, we can simulate typing on body or a generic input if we find one, or just evaluate a DOM insertion)
            # We'll inject an input field via evaluate, then type into it to prove it works.
            print("\n-> Injecting test input field via evaluate...")
            await session.call_tool("evaluate", {"expression": "let inp = document.createElement('input'); inp.id = 'test-input'; document.body.prepend(inp); true"})
            
            print("-> Typing into injected input...")
            type_res = await session.call_tool("type", {"selector": "#test-input", "text": "Phantom Cloud rules!", "clear": True})
            print(f"Type Response: {type_res.content[0].text.strip()}")
            
            # 6. Wait
            print("\n-> Waiting 500ms...")
            wait_res = await session.call_tool("wait", {"delay_ms": 500})
            print(f"Wait Response: {wait_res.content[0].text.strip()}")
            
            # 7. Click (Click the Fingerprint scanner link)
            print(f"\n-> Clicking link {link_ref} ...")
            click_res = await session.call_tool("click", {"ref": link_ref})
            print(f"Click Response: {click_res.content[0].text.strip()}")
            
            print("\n-> 6 Tools Test sequence complete!")

if __name__ == "__main__":
    asyncio.run(main())