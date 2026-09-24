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

PORT = 8765
SERVER_URL = f"http://127.0.0.1:{PORT}"
SSE_URL = f"{SERVER_URL}/sse/?token=ph_live_exhaustive_pool_test"

# Results structure to compile our exhaustive matrix report
results = []

def record_result(pattern_id, name, sequence_step, status, duration_ms, error="", lens_info=""):
    results.append({
        "pattern_id": pattern_id,
        "name": name,
        "step": sequence_step,
        "status": status,
        "duration_ms": duration_ms,
        "error": error,
        "lens_info": lens_info
    })

async def run_step(session, pattern_id, pattern_name, step_num, tool_name, kwargs, expect_error=False):
    t0 = time.perf_counter()
    action_desc = f"{tool_name}({kwargs})"
    print(f"  [Pattern {pattern_id} - Step {step_num}] Calling {tool_name} with {kwargs}...")
    
    try:
        res = await session.call_tool(tool_name, kwargs)
        dt = (time.perf_counter() - t0) * 1000
        
        text = res.content[0].text if res.content else ""
        # Improved error detection: avoid matching text content of page snapshots that happens to have the word "error"
        is_error = res.isError or text.startswith("Errore") or text.startswith("Errore critico:")
        
        if is_error:
            if expect_error:
                status = "PASS (Expected Error)"
                error_msg = text.strip()[:150]
                lens_info = "Graceful error returned"
            else:
                status = "FAIL (Unexpected Error)"
                error_msg = text.strip()[:150]
                lens_info = f"Failed tool call. Res: {text[:100]}"
            print(f"    -> {status} in {dt:.1f}ms. Err: {error_msg}")
            record_result(pattern_id, pattern_name, action_desc, status, dt, error_msg, lens_info)
            return False, text
        else:
            if expect_error:
                status = "FAIL (Expected Error but Succeeded)"
                error_msg = "Expected tool to fail, but it returned success."
                lens_info = "Failed to intercept invalid inputs"
            else:
                status = "PASS"
                error_msg = ""
                # Generate a smart lens based on tool output
                if tool_name == "get_snapshot":
                    # Count refs or elements in the snapshot
                    elements_count = len(re.findall(r"\[(ax\d+|e\d+):", text))
                    char_count = len(text)
                    lens_info = f"Snapshot lens: {char_count} chars, {elements_count} mapped refs."
                elif tool_name == "navigate":
                    lens_info = f"Navigated successfully to {kwargs.get('url')}"
                elif tool_name == "evaluate":
                    lens_info = f"Evaluated result: '{text.strip()[:60]}'"
                else:
                    lens_info = f"Success. Res: '{text.strip()[:60]}'"
            
            print(f"    -> {status} in {dt:.1f}ms. Info: {lens_info}")
            record_result(pattern_id, pattern_name, action_desc, status, dt, error_msg, lens_info)
            return True, text
            
    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000
        status = "PASS (Expected Exception)" if expect_error else "FAIL (Exception Triggered)"
        err_str = f"{type(e).__name__}: {str(e)}"
        print(f"    -> {status} in {dt:.1f}ms. Exception: {err_str}")
        record_result(pattern_id, pattern_name, action_desc, status, dt, err_str, "Connection or schema exception")
        return False, None

async def execute_all_patterns(session):
    print("\n" + "="*80)
    print("BEGINNING EXHAUSTIVE POOL OF TOOL SELECTION PATTERNS")
    print("="*80)

    # --------------------------------------------------------------------------
    # PATTERN 1: Premature Actions (Uninitialized State Error Resilience)
    # --------------------------------------------------------------------------
    p_id, p_name = 1, "Premature Action Handling"
    print(f"\n[Pattern {p_id}] {p_name}")
    # Call evaluate before navigating anywhere (browser/page might be blank/uninitialized)
    await run_step(session, p_id, p_name, 1, "evaluate", {"expression": "document.title"}, expect_error=True)
    await run_step(session, p_id, p_name, 2, "click", {"x": 100, "y": 100}, expect_error=True)

    # --------------------------------------------------------------------------
    # PATTERN 2: Standard Navigation & HTML Snapshot Lens
    # --------------------------------------------------------------------------
    p_id, p_name = 2, "Standard Navigation & HTML Snapshot"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://example.com/"})
    await run_step(session, p_id, p_name, 2, "wait", {"delay_ms": 200})
    success, snap_html = await run_step(session, p_id, p_name, 3, "get_snapshot", {"mode": "html"})

    # --------------------------------------------------------------------------
    # PATTERN 3: Standard Navigation & Native AX Snapshot Lens
    # --------------------------------------------------------------------------
    p_id, p_name = 3, "Standard Navigation & AX Snapshot"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://example.com/"})
    await run_step(session, p_id, p_name, 2, "wait", {"delay_ms": 200})
    success, snap_ax = await run_step(session, p_id, p_name, 3, "get_snapshot", {"mode": "ax"})

    # --------------------------------------------------------------------------
    # PATTERN 4: HTML Ref Element Interaction Sequence
    # --------------------------------------------------------------------------
    p_id, p_name = 4, "HTML Ref Click Sequence"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://example.com/"})
    success, snap = await run_step(session, p_id, p_name, 2, "get_snapshot", {"mode": "html"})
    
    # Extract More Information link reference in HTML mode
    # Standard format: [e2: A href='...'] More information...
    html_match = re.search(r"\[(e\d+):\s*A\s+href='[^']*'\s*\]\s*More information", snap or "", re.IGNORECASE)
    if not html_match:
        html_match = re.search(r"\[(e\d+):\s*A", snap or "", re.IGNORECASE)
    
    html_ref = html_match.group(1) if html_match else "e1"
    print(f"    -> Extracted HTML link ref: {html_ref}")
    
    await run_step(session, p_id, p_name, 3, "click", {"ref": html_ref})
    await run_step(session, p_id, p_name, 4, "wait", {"delay_ms": 1000}) # Allow transition
    await run_step(session, p_id, p_name, 5, "evaluate", {"expression": "window.location.href"})

    # --------------------------------------------------------------------------
    # PATTERN 5: Native AX Ref Element Interaction Sequence
    # --------------------------------------------------------------------------
    p_id, p_name = 5, "AX Ref Click Sequence"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://example.com/"})
    success, snap = await run_step(session, p_id, p_name, 2, "get_snapshot", {"mode": "ax"})
    
    # Extract More Information link reference in AX mode
    # Standard format: [ax12: LINK 'More information...']
    ax_match = re.search(r"\[(ax\d+):\s*LINK\s+'More information\.\.\.'\]", snap or "", re.IGNORECASE)
    if not ax_match:
        ax_match = re.search(r"\[(ax\d+):\s*LINK", snap or "", re.IGNORECASE)
        
    ax_ref = ax_match.group(1) if ax_match else "ax1"
    print(f"    -> Extracted AX link ref: {ax_ref}")
    
    await run_step(session, p_id, p_name, 3, "click", {"ref": ax_ref})
    await run_step(session, p_id, p_name, 4, "wait", {"delay_ms": 1000}) # Allow transition
    await run_step(session, p_id, p_name, 5, "evaluate", {"expression": "window.location.href"})

    # --------------------------------------------------------------------------
    # PATTERN 6: Target Swap & State Persistence
    # --------------------------------------------------------------------------
    p_id, p_name = 6, "Target Swap Persistence"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://example.com/"})
    # Target swap navigation to bot.sannysoft.com
    await run_step(session, p_id, p_name, 2, "navigate", {"url": "https://bot.sannysoft.com/"})
    await run_step(session, p_id, p_name, 3, "wait", {"delay_ms": 1500})
    await run_step(session, p_id, p_name, 4, "evaluate", {"expression": "window.location.host"})

    # --------------------------------------------------------------------------
    # PATTERN 7: Controlled Non-Destructive Sannysoft Interaction
    # --------------------------------------------------------------------------
    p_id, p_name = 7, "Sannysoft Safe Interactive Type/Click"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://bot.sannysoft.com/"})
    
    # Inject an input field safely via evaluate, setting aria-label for bulletproof AX tracking
    print("    [Adapter] Injecting safe test input element with explicit aria-label...")
    inject_js = """
    let inp = document.createElement('input'); 
    inp.id = 'safe-phantom-input'; 
    inp.setAttribute('aria-label', 'Safe Phantom Input');
    inp.style.position = 'fixed'; 
    inp.style.top = '10px'; 
    inp.style.left = '10px'; 
    inp.style.zIndex = '99999'; 
    document.body.prepend(inp); 
    true
    """
    await run_step(session, p_id, p_name, 2, "evaluate", {"expression": inject_js})
    
    # Get AX Snapshot to find our injected input reference
    success, snap = await run_step(session, p_id, p_name, 3, "get_snapshot", {"mode": "ax"})
    
    # Find our injected input element using the explicit aria-label
    input_match = re.search(r"\[(ax\d+):\s*TEXTBOX\s+'Safe Phantom Input'[^\]]*\]", snap or "", re.IGNORECASE)
    input_ref = input_match.group(1) if input_match else None
    
    if input_ref:
        print(f"    -> Extracted injected input AX ref: {input_ref}")
        # Type into the injected input
        await run_step(session, p_id, p_name, 4, "type", {"ref": input_ref, "text": "Phantom Evasion Verified", "clear": True})
    else:
        print("    -> Injected input AX ref not matched dynamically. Falling back to selector-based interaction.")
        await run_step(session, p_id, p_name, 4, "type", {"selector": "#safe-phantom-input", "text": "Phantom Evasion Verified", "clear": True})
        
    # Verify the input text value is matches via evaluate
    await run_step(session, p_id, p_name, 5, "evaluate", {"expression": "document.getElementById('safe-phantom-input').value"})

    # --------------------------------------------------------------------------
    # PATTERN 8: Multi-step Async Wait & Viewport Telemetry
    # --------------------------------------------------------------------------
    p_id, p_name = 8, "Async Wait & Viewport Sequence"
    print(f"\n[Pattern {p_id}] {p_name}")
    await run_step(session, p_id, p_name, 1, "navigate", {"url": "https://example.com/"})
    
    # Inject delayed element (500ms delay)
    inject_delayed_js = "setTimeout(() => { let div = document.createElement('div'); div.id = 'delayed-phantom-div'; div.textContent = 'Found!'; document.body.appendChild(div); }, 500); true"
    await run_step(session, p_id, p_name, 2, "evaluate", {"expression": inject_delayed_js})
    
    # Call wait to synchronize with the element
    await run_step(session, p_id, p_name, 3, "wait", {"selector": "#delayed-phantom-div", "timeout_ms": 3000})
    
    # Check the viewport scroll action
    await run_step(session, p_id, p_name, 4, "evaluate", {"expression": "window.scrollBy(0, 500); 'scrolled_down_500px'"})

    # --------------------------------------------------------------------------
    # PATTERN 9: Argument Integrity and Error Resilience
    # --------------------------------------------------------------------------
    p_id, p_name = 9, "Argument Integrity & Validation"
    print(f"\n[Pattern {p_id}] {p_name}")
    # Missing required arguments for navigate
    await run_step(session, p_id, p_name, 1, "navigate", {}, expect_error=True)
    # Missing all arguments for click (requires ref, selector, or x/y)
    await run_step(session, p_id, p_name, 2, "click", {}, expect_error=True)
    # Call an unregistered tool (should fail cleanly in client-server validation)
    await run_step(session, p_id, p_name, 3, "invalid_nonexistent_tool", {"arg": "val"}, expect_error=True)


async def main():
    print("="*80)
    print("PHANTOM_CLOUD EXHAUSTIVE TOOL SELECTION PATTERN POOL")
    print("="*80)
    
    server_proc = None
    python_bin = os.path.abspath(".venv/bin/python")
    server_script = os.path.abspath("phantom_cloud.py")
    
    # Stage 1: Pre-cleanup of any existing processes to ensure fresh start
    print("\n[Step 1] Executing pre-start process cleanup...")
    subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "Xvfb"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "phantom_cloud.py"], capture_output=True)
    print("Pre-cleanup finished successfully.")

    try:
        # Stage 2: Start Starlette Server under Xvfb-run on port 8765
        print(f"\n[Step 2] Launching phantom_cloud server on port {PORT} with Xvfb-run...")
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
        
        server_proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid # Create process group to ensure clean teardown
        )
        print(f"Server subprocess started. PID: {server_proc.pid}")
        
        # Stage 3: Poll Health Check Endpoint
        print("\n[Step 3] Polling health check endpoint...")
        health_ok = False
        async with httpx.AsyncClient() as client:
            for attempt in range(40): # Poll for up to 20 seconds
                try:
                    resp = await client.get(SERVER_URL, timeout=1.0)
                    if resp.status_code == 200:
                        health_ok = True
                        print(f"Health check succeeded (200 OK) after {attempt*0.5:.1f} seconds.")
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)
                
        if not health_ok:
            raise RuntimeError("Server health check failed to respond 200 OK after 20 seconds.")
        
        # Stage 4: Connect via MCP SSE Client & Initialize ClientSession
        print(f"\n[Step 4] Connecting MCP client to SSE at {SSE_URL}...")
        async with sse_client(SSE_URL, headers={}) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Session initialized successfully! Executing test pools...")
                
                # Execute all 9 multi-step patterns
                await execute_all_patterns(session)

    except Exception as e:
        print(f"\nCRITICAL EXCEPTION IN POOL CONTROLLER: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Stage 5: Teardown and clean up processes
        print("\n" + "="*80)
        print("PERFORMING COMPREHENSIVE TEARDOWN...")
        print("="*80)
        
        # Kill server process group if started
        if server_proc:
            try:
                print(f"Terminating server process group (PGID: {server_proc.pid})...")
                os.killpg(os.getpgid(server_proc.pid), signal.SIGKILL)
                server_proc.wait(timeout=2.0)
                print("Server process group terminated.")
            except Exception as ex:
                print(f"Failed to kill process group cleanly: {str(ex)}")
                
        # Force-kill any leftover processes
        print("Force-killing any remaining chrome, chromium, xvfb, or phantom_cloud python processes...")
        subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", "Xvfb"], capture_output=True)
        subprocess.run(["pkill", "-9", "-f", "phantom_cloud.py"], capture_output=True)
        print("Comprehensive cleanup complete.")
        
        # Compile and print the Markdown Report
        print("\n" + "#"*80)
        print("                      EXHAUSTIVE PATTERN POOL REPORT")
        print("#"*80)
        print("\n| Pattern ID | Pattern Name | Step Executed | Status | Duration (ms) | Lens Info / Notes | Errors (if any) |")
        print("|---|---|---|---|---|---|---|")
        for res in results:
            err_disp = res["error"] if res["error"] else "-"
            print(f"| {res['pattern_id']} | {res['name']} | `{res['step']}` | **{res['status']}** | {res['duration_ms']:.1f}ms | {res['lens_info']} | {err_disp} |")
        print("\n" + "#"*80)

if __name__ == "__main__":
    asyncio.run(main())
