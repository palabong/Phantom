import os
import sys
import time
import asyncio
import subprocess
import httpx
import re
import signal
from mcp.client.sse import sse_client
from mcp import ClientSession

# Standard port for local tests
PORT = 8000
SERVER_URL = f"http://127.0.0.1:{PORT}"
SSE_URL = f"{SERVER_URL}/sse/?token=ph_live_test_cold_start"

async def main():
    print("="*60)
    print("PHANTOM_CLOUD: PRODUCTION-ALIGNED LOCAL COLD START & VERIFICATION")
    print("="*60)
    
    server_proc = None
    timings = {}
    steps_status = []
    
    # Absolute paths
    python_bin = os.path.abspath(".venv/bin/python")
    server_script = os.path.abspath("phantom_cloud.py")
    test_page = os.path.abspath("tests/test_page.html")
    test_page_url = f"file://{test_page}"
    
    print(f"Python path: {python_bin}")
    print(f"Server script: {server_script}")
    print(f"Test page URL: {test_page_url}")
    
    # Stage 1: Pre-cleanup of any existing processes to ensure fresh cold start
    print("\n[Step 1] Executing pre-start process cleanup...")
    start_cleanup = time.perf_counter()
    subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "Xvfb"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "phantom_cloud.py"], capture_output=True)
    cleanup_duration = time.perf_counter() - start_cleanup
    timings["Pre-cleanup"] = cleanup_duration
    print(f"Pre-cleanup finished in {cleanup_duration:.2f}s.")
    steps_status.append(("Pre-cleanup", "N/A", f"{cleanup_duration:.3f}s", "PASS"))

    try:
        # Stage 2: Start Starlette Server under Xvfb-run (production-aligned environment)
        print("\n[Step 2] Launching phantom_cloud server in production-aligned mode...")
        env = os.environ.copy()
        env["PORT"] = str(PORT)
        env["UNKEY_ROOT_KEY"] = "" # Trigger fallback authentication locally
        
        cmd = [
            "xvfb-run",
            "-a",
            "--server-args=-screen 0 1920x1080x24",
            python_bin,
            server_script
        ]
        
        start_launch = time.perf_counter()
        server_proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid # Create process group to ensure clean teardown
        )
        server_pid = server_proc.pid
        print(f"Server subprocess started. PID: {server_pid}")
        
        # Stage 3: Poll Health Check Endpoint (Cold Start Time)
        print("\n[Step 3] Polling health check endpoint...")
        health_ok = False
        health_code = None
        server_start_duration = 0
        
        async with httpx.AsyncClient() as client:
            for attempt in range(40): # Poll for up to 20 seconds
                try:
                    resp = await client.get(SERVER_URL, timeout=1.0)
                    health_code = resp.status_code
                    if resp.status_code == 200:
                        health_ok = True
                        server_start_duration = time.perf_counter() - start_launch
                        print(f"Health check succeeded (200 OK) in {server_start_duration:.2f}s.")
                        print(f"Response: {resp.text.strip()}")
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)
                
        if not health_ok:
            raise RuntimeError(f"Server health check failed to respond 200 OK after 20 seconds. Last code: {health_code}")
            
        timings["Server Cold Start"] = server_start_duration
        steps_status.append(("Server Cold Start", str(health_code), f"{server_start_duration:.3f}s", "PASS"))
        
        # Stage 4: Connect via MCP SSE Client & Initialize ClientSession
        print("\n[Step 4] Connecting MCP client to server SSE endpoint...")
        start_mcp = time.perf_counter()
        
        headers = {}
        async with sse_client(SSE_URL, headers=headers) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                print("Connected to SSE. Initializing MCP Client Session...")
                await session.initialize()
                mcp_init_duration = time.perf_counter() - start_mcp
                timings["MCP Init"] = mcp_init_duration
                steps_status.append(("MCP Init Connection", "200", f"{mcp_init_duration:.3f}s", "PASS"))
                
                # List tools and verify there are exactly 6 tools registered
                print("\n[Step 5] Listing registered tools...")
                start_list = time.perf_counter()
                tools_res = await session.list_tools()
                list_duration = time.perf_counter() - start_list
                
                tool_names = [tool.name for tool in tools_res.tools]
                print(f"Registered tools: {tool_names}")
                
                expected_tools = ["navigate", "get_snapshot", "click", "type", "evaluate", "wait"]
                all_tools_present = all(t in tool_names for t in expected_tools)
                
                if all_tools_present and len(tools_res.tools) == 6:
                    print("All 6 standard and interaction tools are registered correctly!")
                    steps_status.append(("List Tools (6 tools verified)", "200", f"{list_duration:.3f}s", "PASS"))
                else:
                    print(f"Error: Registered tools {tool_names} do not match the expected 6 tools.")
                    steps_status.append(("List Tools", "200", f"{list_duration:.3f}s", "FAIL"))
                    raise ValueError("Incorrect tool registration count")
                
                # Tool 1: navigate to local test page (WAF evasion bypass mode test)
                print(f"\n[Step 6] Executing tool: navigate -> {test_page_url}")
                start_tool = time.perf_counter()
                nav_res = await session.call_tool("navigate", {"url": test_page_url})
                tool_duration = time.perf_counter() - start_tool
                print(f"Response: {nav_res.content[0].text.strip()}")
                steps_status.append(("Tool: navigate", "200", f"{tool_duration:.3f}s", "PASS"))
                
                # Tool 2: get_snapshot in native 'ax' mode
                print("\n[Step 7] Executing tool: get_snapshot (AX mode)...")
                start_tool = time.perf_counter()
                snap_res = await session.call_tool("get_snapshot", {"mode": "ax"})
                tool_duration = time.perf_counter() - start_tool
                snapshot_text = snap_res.content[0].text
                print(f"Snapshot received (len {len(snapshot_text)}):\n{snapshot_text}\n")
                steps_status.append(("Tool: get_snapshot (ax)", "200", f"{tool_duration:.3f}s", "PASS"))
                
                # Parse AX references from snapshot text using regular expressions
                print("Parsing AX tree elements for interactive references...")
                button_ref_match = re.search(r"\[(ax\d+):\s*BUTTON\s+'Click Me'\]", snapshot_text, re.IGNORECASE)
                input_ref_match = re.search(r"\[(ax\d+):\s*[A-Z_]+\s+'Enter text'[^\]]*\]", snapshot_text, re.IGNORECASE)
                
                if not button_ref_match or not input_ref_match:
                    # Generic lookup if exact casing/role varies
                    button_ref_match = re.search(r"\[(ax\d+):\s*\w+\s+'Click Me'\]", snapshot_text, re.IGNORECASE)
                    input_ref_match = re.search(r"\[(ax\d+):\s*\w+\s+'Enter text'[^\]]*\]", snapshot_text, re.IGNORECASE)
                
                if button_ref_match:
                    button_ref = button_ref_match.group(1)
                    print(f"Found Button reference: {button_ref}")
                else:
                    button_ref = "ax1" # Fallback
                    print("Warning: Button AX reference not matched dynamically. Using fallback 'ax1'.")
                    
                if input_ref_match:
                    input_ref = input_ref_match.group(1)
                    print(f"Found Input reference: {input_ref}")
                else:
                    input_ref = "ax2" # Fallback
                    print("Warning: Input AX reference not matched dynamically. Using fallback 'ax2'.")
                
                # Tool 3: wait (static delay test)
                print("\n[Step 8] Executing tool: wait (delay_ms=500)...")
                start_tool = time.perf_counter()
                wait_res = await session.call_tool("wait", {"delay_ms": 500})
                tool_duration = time.perf_counter() - start_tool
                print(f"Response: {wait_res.content[0].text.strip()}")
                steps_status.append(("Tool: wait", "200", f"{tool_duration:.3f}s", "PASS"))
                
                # Tool 4: type text using the AX reference
                print(f"\n[Step 9] Executing tool: type -> text='Phantom Cold Start' using reference {input_ref}")
                start_tool = time.perf_counter()
                type_res = await session.call_tool("type", {"ref": input_ref, "text": "Phantom Cold Start", "clear": True})
                tool_duration = time.perf_counter() - start_tool
                print(f"Response: {type_res.content[0].text.strip()}")
                steps_status.append(("Tool: type", "200", f"{tool_duration:.3f}s", "PASS"))
                
                # Tool 5: evaluate JS to verify type tool effect (input should change document title)
                print("\n[Step 10] Executing tool: evaluate -> document.title to verify type action...")
                start_tool = time.perf_counter()
                eval_res = await session.call_tool("evaluate", {"expression": "document.title"})
                tool_duration = time.perf_counter() - start_tool
                title_val = eval_res.content[0].text.strip().strip('"')
                print(f"Evaluated Document Title: '{title_val}'")
                
                if title_val == "Phantom Cold Start":
                    print("Title matched 'Phantom Cold Start'! Type action verified successfully!")
                    steps_status.append(("Tool: evaluate (verify type)", "200", f"{tool_duration:.3f}s", "PASS"))
                else:
                    print(f"Error: Title was '{title_val}', expected 'Phantom Cold Start'")
                    steps_status.append(("Tool: evaluate (verify type)", "200", f"{tool_duration:.3f}s", "FAIL"))
                
                # Tool 6: click button using AX reference
                print(f"\n[Step 11] Executing tool: click using reference {button_ref}")
                start_tool = time.perf_counter()
                click_res = await session.call_tool("click", {"ref": button_ref})
                tool_duration = time.perf_counter() - start_tool
                print(f"Response: {click_res.content[0].text.strip()}")
                steps_status.append(("Tool: click", "200", f"{tool_duration:.3f}s", "PASS"))
                
                # Verify click tool effect via evaluate
                print("\n[Step 12] Executing tool: evaluate -> document.title to verify click action...")
                start_tool = time.perf_counter()
                eval_res = await session.call_tool("evaluate", {"expression": "document.title"})
                tool_duration = time.perf_counter() - start_tool
                title_val = eval_res.content[0].text.strip().strip('"')
                print(f"Evaluated Document Title: '{title_val}'")
                
                if title_val == "Button Clicked":
                    print("Title matched 'Button Clicked'! Click action verified successfully!")
                    steps_status.append(("Tool: evaluate (verify click)", "200", f"{tool_duration:.3f}s", "PASS"))
                else:
                    print(f"Error: Title was '{title_val}', expected 'Button Clicked'")
                    steps_status.append(("Tool: evaluate (verify click)", "200", f"{tool_duration:.3f}s", "FAIL"))

    except Exception as e:
        print(f"\nCRITICAL FAIL DURING INTEGRATION TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        steps_status.append(("Integration Flow Exception", "500", "N/A", "FAIL"))
    finally:
        # Stage 13: Clean Teardown of Chrome, Xvfb, and Server processes
        print("\n" + "="*60)
        print("PERFORMING CLEAN TEARDOWN...")
        print("="*60)
        
        # Kill server process group if started
        if server_proc:
            try:
                print(f"Terminating server process group (PGID: {server_proc.pid})...")
                os.killpg(os.getpgid(server_proc.pid), signal.SIGKILL)
                server_proc.wait(timeout=2.0)
            except Exception as ex:
                print(f"Failed to kill process group cleanly: {str(ex)}")
                
        # Mandatory teardown of any orphaned processes
        print("Force-killing any orphaned chrome, chromium, xvfb, or python phantom_cloud.py processes...")
        subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", "Xvfb"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", "phantom_cloud.py"], capture_output=True)
        
        print("\nVerification process complete. Displaying status table:")
        print("\n" + "-"*80)
        print(f"{'Step / Phase':<35} | {'HTTP Code':<10} | {'Timing':<12} | {'Status':<10}")
        print("-"*80)
        for step, h_code, timing, status in steps_status:
            print(f"{step:<35} | {h_code:<10} | {timing:<12} | {status:<10}")
        print("-"*80)
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
