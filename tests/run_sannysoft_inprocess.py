import os
import sys
import time
import asyncio
import subprocess
import re
import signal

# Add current directory to path just in case
sys.path.insert(0, os.path.abspath("."))

from phantom_cloud import handle_list_tools, handle_call_tool, state

async def main():
    print("="*60)
    print("IN-PROCESS MCP TOOL SEQUENCE TESTS (SANNYSOFT)")
    print("="*60)

    # 1) PRE-CLEANUP (Executed inside the python process before running test loop)
    print("[1/5] Executing pre-cleanup of Chrome, Xvfb and python servers...")
    subprocess.run(["pkill", "-9", "-f", "python.*phantom_cloud.py"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "Google Chrome|google-chrome|Chromium"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "Xvfb"], capture_output=True)
    await asyncio.sleep(1)
    print("Cleanup complete.")

    # 2) IMPORT & LIST TOOLS
    print("\n[2/5] Verification of registered tools...")
    tools = await handle_list_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Registered tool names: {tool_names}")
    expected_tools = ["navigate", "get_snapshot", "click", "type", "evaluate", "wait"]
    
    # Assert exact match (ignoring order)
    assert sorted(tool_names) == sorted(expected_tools), f"Error: Registered tools {tool_names} do not match {expected_tools}"
    print("Assertion PASSED: All 6 standard tools are registered and matched exactly.")

    # 3) FULL 6-TOOL RUN
    print("\n[3/5] Commencing 6-tool run sequence against bot.sannysoft.com...")
    
    report = {}
    
    # Helper to call and measure tool execution in-process
    async def call_inprocess(name, args):
        t0 = time.perf_counter()
        try:
            res = await handle_call_tool(name, args)
            dt = (time.perf_counter() - t0) * 1000
            text = res[0].text if res else ""
            is_error = text.startswith("Errore") or text.startswith("Errore critico:")
            return is_error, text, dt
        except Exception as e:
            dt = (time.perf_counter() - t0) * 1000
            return True, f"Exception: {str(e)}", dt

    # a) navigate
    print("\n  -> Tool a: navigate (https://bot.sannysoft.com/)...")
    is_err, res_text, dt = await call_inprocess("navigate", {"url": "https://bot.sannysoft.com/"})
    ok_str = "fail" if is_err else "ok"
    report["navigate"] = {"ok": ok_str, "ms": dt, "note": "Navigated successfully" if not is_err else res_text[:100]}
    print(f"     Status: {ok_str.upper()} | Time: {dt:.1f}ms")

    # b) get_snapshot html
    print("\n  -> Tool b: get_snapshot (mode='html')...")
    is_err, html_snap, dt = await call_inprocess("get_snapshot", {"mode": "html"})
    ok_str = "fail" if is_err else "ok"
    report["get_snapshot html"] = {"ok": ok_str, "ms": dt, "note": f"len={len(html_snap)}"}
    print(f"     Status: {ok_str.upper()} | Time: {dt:.1f}ms | Length: {len(html_snap)}")

    # 4) RECORD BOOLEAN PRESENCE OF KEY SANNYSOFT CRITERIA
    missing_passed = "missing (passed)" in html_snap
    swift_shader = "SwiftShader" in html_snap
    web_driver = "WebDriver" in html_snap
    print(f"\n[4/5] Recording Sannysoft Evasion Signal presence in HTML snapshot:")
    print(f"      missing (passed): {missing_passed}")
    print(f"      SwiftShader:      {swift_shader}")
    print(f"      WebDriver:        {web_driver}")

    # c) get_snapshot ax
    print("\n  -> Tool c: get_snapshot (mode='ax')...")
    is_err, ax_snap, dt = await call_inprocess("get_snapshot", {"mode": "ax"})
    ok_str = "fail" if is_err else "ok"
    report["get_snapshot ax"] = {"ok": ok_str, "ms": dt, "note": f"len={len(ax_snap)}"}
    print(f"     Status: {ok_str.upper()} | Time: {dt:.1f}ms | Length: {len(ax_snap)}")

    # d) evaluate
    print("\n  -> Tool d: evaluate (document.title)...")
    is_err, eval_res, dt = await call_inprocess("evaluate", {"expression": "document.title"})
    ok_str = "fail" if is_err else "ok"
    report["evaluate"] = {"ok": ok_str, "ms": dt, "note": f"title={eval_res.strip()}"}
    print(f"     Status: {ok_str.upper()} | Time: {dt:.1f}ms | Title: {eval_res.strip()}")

    # e) wait
    print("\n  -> Tool e: wait (delay_ms=300)...")
    is_err, wait_res, dt = await call_inprocess("wait", {"delay_ms": 300})
    ok_str = "fail" if is_err else "ok"
    report["wait"] = {"ok": ok_str, "ms": dt, "note": "Delay wait completed"}
    print(f"     Status: {ok_str.upper()} | Time: {dt:.1f}ms")

    # f) click (miss) - expected controlled failure
    print("\n  -> Tool f: click (miss) CSS #phantom-nonexistent-xyz...")
    is_err, click_miss_res, dt = await call_inprocess("click", {"selector": "#phantom-nonexistent-xyz"})
    # Since we EXPECT a controlled failure (element not found), the tool execution successfully handled it.
    controlled_fail = is_err and "non trovato" in click_miss_res
    ok_str = "ok" if controlled_fail else "fail"
    report["click (miss)"] = {"ok": ok_str, "ms": dt, "note": f"controlled fail: {'yes' if controlled_fail else 'no'} ({click_miss_res[:50]})"}
    print(f"     Status: {ok_str.upper()} (Controlled Fail: {'YES' if controlled_fail else 'NO'}) | Time: {dt:.1f}ms")

    # g) Optional click
    print("\n  -> Tool g: Optional click ref...")
    # Let's search the AX snapshot for a safe link ref
    link_match = re.search(r"\[(ax\d+):\s*LINK\s+'Fingerprint Scanner'\]", ax_snap, re.IGNORECASE)
    if link_match:
        ax_ref = link_match.group(1)
        print(f"     Found safe link reference 'Fingerprint Scanner' at {ax_ref}. Executing click...")
        opt_err, opt_res, opt_dt = await call_inprocess("click", {"ref": ax_ref})
        opt_ok = "ok" if not opt_err else "fail"
        report["optional click"] = {"ok": opt_ok, "ms": opt_dt, "note": f"Clicked {ax_ref} -> {opt_res[:60]}"}
        print(f"     Status: {opt_ok.upper()} | Time: {opt_dt:.1f}ms | Res: {opt_res}")
    else:
        # Fallback to check html mode
        html_link_match = re.search(r"\[(e\d+):\s*A[^\]]*\]", html_snap, re.IGNORECASE)
        if html_link_match:
            html_ref = html_link_match.group(1)
            print(f"     Found first HTML anchor ref {html_ref}. Executing click...")
            opt_err, opt_res, opt_dt = await call_inprocess("click", {"ref": html_ref})
            opt_ok = "ok" if not opt_err else "fail"
            report["optional click"] = {"ok": opt_ok, "ms": opt_dt, "note": f"Clicked {html_ref} -> {opt_res[:60]}"}
            print(f"     Status: {opt_ok.upper()} | Time: {opt_dt:.1f}ms | Res: {opt_res}")
        else:
            report["optional click"] = {"ok": "ok", "ms": 0.0, "note": "SKIPPED"}
            print("     No safe interactive links found in snapshots. Optional click SKIPPED.")

    # 5) TEARDOWN
    print("\n[5/5] Performing comprehensive teardown...")
    t_start = time.perf_counter()
    if state.browser:
        try:
            print("      Stopping state.browser...")
            state.browser.stop()
            print("      state.browser stopped.")
        except Exception as e:
            print(f"      Error stopping state.browser: {str(e)}")
            
    # Force kill leftover processes
    subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "Xvfb"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "phantom_cloud.py"], capture_output=True)
    
    # Confirm no phantom_cloud.py left
    pg_res = subprocess.run(["pgrep", "-f", "phantom_cloud.py"], capture_output=True, text=True)
    active_pids = [pid.strip() for pid in pg_res.stdout.split() if pid.strip() and int(pid.strip()) != os.getpid()]
    teardown_clean = len(active_pids) == 0
    print(f"      Teardown Clean: {'YES' if teardown_clean else 'NO'} (Remaining phantom PIDs: {active_pids})")

    # 6) FINAL REPORT
    print("\n" + "#"*60)
    print("                           FINAL REPORT")
    print("#"*60)
    print("\n| tool | ok | ms | note |")
    print("|---|---|---|---|")
    print(f"| navigate | {report['navigate']['ok']} | {report['navigate']['ms']:.1f} | {report['navigate']['note']} |")
    print(f"| get_snapshot html | {report['get_snapshot html']['ok']} | {report['get_snapshot html']['ms']:.1f} | {report['get_snapshot html']['note']} |")
    print(f"| get_snapshot ax | {report['get_snapshot ax']['ok']} | {report['get_snapshot ax']['ms']:.1f} | {report['get_snapshot ax']['note']} |")
    print(f"| evaluate | {report['evaluate']['ok']} | {report['evaluate']['ms']:.1f} | {report['evaluate']['note']} |")
    print(f"| wait | {report['wait']['ok']} | {report['wait']['ms']:.1f} | {report['wait']['note']} |")
    print(f"| click (miss) | {report['click (miss)']['ok']} | {report['click (miss)']['ms']:.1f} | {report['click (miss)']['note']} |")
    if "optional click" in report:
        print(f"| optional click | {report['optional click']['ok']} | {report['optional click']['ms']:.1f} | {report['optional click']['note']} |")
    
    print(f"\nSignals: missing_passed={str(missing_passed).lower()}  SwiftShader={str(swift_shader).lower()}  WebDriver={str(web_driver).lower()}")
    print(f"Teardown: clean={'yes' if teardown_clean else 'no'}")
    print("Explicit: no code changes, no deploy")
    print("#"*60)

if __name__ == "__main__":
    asyncio.run(main())
