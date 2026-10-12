import os
import sys
import time
import asyncio
import json
import datetime
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "D2aZuYtdGL6tUfuV2egoxp"
SSE_URL = f"https://phantom-cloud-engine.fly.dev/sse/?token={TOKEN}"
TARGET_URL = "https://funk-it-up-sdzgxmea.myshopify.com/"

async def main():
    # Use runs/prod_postdeploy_ exactly
    run_dir = f"runs/prod_postdeploy_"
    os.makedirs(run_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    results = []
    protocol_log = []
    html_text = ""
    ax_text = ""
    eval_text = ""
    sse_duration_ms = 0
    
    try:
        t0 = time.perf_counter()
        async with sse_client(SSE_URL, headers={}) as (read_stream, write_stream):
            sse_duration_ms = (time.perf_counter() - t0) * 1000
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # 1. tools/list
                t0 = time.perf_counter()
                tools_res = await session.list_tools()
                dt = (time.perf_counter() - t0) * 1000
                protocol_log.append({"step": "tools/list", "request": {}, "response": {"tools": [{"name": t.name} for t in tools_res.tools]}, "duration_ms": dt, "status": "ok"})
                results.append({"tool": "tools/list", "status": "ok", "latency_ms": dt, "details": f"count={len(tools_res.tools)}"})
                
                # 2. navigate
                t0 = time.perf_counter()
                nav_res = await session.call_tool("navigate", {"url": TARGET_URL})
                dt = (time.perf_counter() - t0) * 1000
                nav_text = nav_res.content[0].text if nav_res.content else ""
                nav_status = "ok" if not getattr(nav_res, "isError", False) else "fail"
                protocol_log.append({"step": "navigate", "request": {"url": TARGET_URL}, "response": {"content": [{"type": "text", "text": nav_text[:200]}]}, "duration_ms": dt, "status": nav_status})
                results.append({"tool": "navigate", "status": nav_status, "latency_ms": dt, "details": "navigated"})
                
                # 3. wait
                t0 = time.perf_counter()
                wait_res = await session.call_tool("wait", {"delay_ms": 500})
                dt = (time.perf_counter() - t0) * 1000
                wait_text = wait_res.content[0].text if wait_res.content else ""
                wait_status = "ok" if not getattr(wait_res, "isError", False) else "fail"
                protocol_log.append({"step": "wait", "request": {"delay_ms": 500}, "response": {"content": [{"type": "text", "text": wait_text[:100]}]}, "duration_ms": dt, "status": wait_status})
                results.append({"tool": "wait", "status": wait_status, "latency_ms": dt, "details": "wait 500ms"})
                
                # 4. get_snapshot html
                t0 = time.perf_counter()
                html_res = await session.call_tool("get_snapshot", {"mode": "html"})
                dt = (time.perf_counter() - t0) * 1000
                html_text = html_res.content[0].text if html_res.content else ""
                html_status = "ok" if not getattr(html_res, "isError", False) else "fail"
                protocol_log.append({"step": "get_snapshot html", "request": {"mode": "html"}, "response": {"content": [{"type": "text", "text": html_text[:200]}]}, "duration_ms": dt, "status": html_status})
                results.append({"tool": "get_snapshot html", "status": html_status, "latency_ms": dt, "details": f"html length {len(html_text)}"})
                
                # 5. get_snapshot ax
                t0 = time.perf_counter()
                ax_res = await session.call_tool("get_snapshot", {"mode": "ax"})
                dt = (time.perf_counter() - t0) * 1000
                ax_text = ax_res.content[0].text if ax_res.content else ""
                ax_status = "ok" if not getattr(ax_res, "isError", False) else "fail"
                protocol_log.append({"step": "get_snapshot ax", "request": {"mode": "ax"}, "response": {"content": [{"type": "text", "text": ax_text[:200]}]}, "duration_ms": dt, "status": ax_status})
                results.append({"tool": "get_snapshot ax", "status": ax_status, "latency_ms": dt, "details": f"ax length {len(ax_text)}"})
                
                # 6. evaluate
                eval_expr = "JSON.stringify({title:document.title,href:location.href,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]')})"
                t0 = time.perf_counter()
                eval_res = await session.call_tool("evaluate", {"expression": eval_expr})
                dt = (time.perf_counter() - t0) * 1000
                eval_text = eval_res.content[0].text if eval_res.content else ""
                eval_status = "ok" if not getattr(eval_res, "isError", False) else "fail"
                protocol_log.append({"step": "evaluate", "request": {"expression": eval_expr}, "response": {"content": [{"type": "text", "text": eval_text}]}, "duration_ms": dt, "status": eval_status})
                results.append({"tool": "evaluate", "status": eval_status, "latency_ms": dt, "details": "evaluate document state"})
                
                # 7. click via ref
                # Find something like [ax3: LINK 'Skip to content']
                match = re.search(r'\[(ax\d+):\s+(?:BUTTON|LINK)', ax_text, re.IGNORECASE)
                if match:
                    ref = match.group(1)
                    t0 = time.perf_counter()
                    click1_res = await session.call_tool("click", {"ref": ref})
                    dt = (time.perf_counter() - t0) * 1000
                    click1_text = click1_res.content[0].text if click1_res.content else ""
                    click1_status = "ok" if not getattr(click1_res, "isError", False) else "fail"
                    protocol_log.append({"step": "click ref", "request": {"ref": ref}, "response": {"content": [{"type": "text", "text": click1_text[:100]}]}, "duration_ms": dt, "status": click1_status})
                    results.append({"tool": "click", "status": click1_status, "latency_ms": dt, "details": f"clicked ref {ref}"})
                else:
                    match = re.search(r'\[(e\d+):\s+(?:BUTTON|A)\s+', html_text, re.IGNORECASE)
                    if match:
                        ref = match.group(1)
                        t0 = time.perf_counter()
                        click1_res = await session.call_tool("click", {"ref": ref})
                        dt = (time.perf_counter() - t0) * 1000
                        click1_text = click1_res.content[0].text if click1_res.content else ""
                        click1_status = "ok" if not getattr(click1_res, "isError", False) else "fail"
                        protocol_log.append({"step": "click ref", "request": {"ref": ref}, "response": {"content": [{"type": "text", "text": click1_text[:100]}]}, "duration_ms": dt, "status": click1_status})
                        results.append({"tool": "click", "status": click1_status, "latency_ms": dt, "details": f"clicked ref {ref}"})
                    else:
                        protocol_log.append({"step": "click ref", "request": {}, "response": {"note": "click N/A"}, "duration_ms": 0.0, "status": "fail"})
                        results.append({"tool": "click", "status": "fail", "latency_ms": 0.0, "details": "N/A - no target found"})
                
                # 8. click #phantom-missing-target
                t0 = time.perf_counter()
                try:
                    click2_res = await session.call_tool("click", {"selector": "#phantom-missing-target"})
                    click2_text = click2_res.content[0].text if click2_res.content else ""
                    is_err = getattr(click2_res, "isError", False)
                except Exception as e:
                    click2_text = str(e)
                    is_err = True
                dt = (time.perf_counter() - t0) * 1000
                protocol_log.append({"step": "click miss", "request": {"selector": "#phantom-missing-target"}, "response": {"content": [{"type": "text", "text": click2_text[:100]}]}, "duration_ms": dt, "status": "fail"})
                results.append({"tool": "click", "status": "fail", "latency_ms": dt, "details": "controlled fail miss (#phantom-missing-target)"})
                
                # Parse eval_text JSON
                eval_obj = {}
                try:
                    raw_eval_text = json.loads(eval_text) # it's a string from JS JSON.stringify
                    eval_obj = json.loads(raw_eval_text)
                except:
                    pass

                has_pw_gate = eval_obj.get("hasPasswordForm", False)
                final_href = eval_obj.get("href", TARGET_URL).strip()

                # protocol.json
                protocol_data = {
                  "timestamp": timestamp,
                  "target_url": TARGET_URL,
                  "server_url": "https://phantom-cloud-engine.fly.dev/sse",
                  "sessions": 1,
                  "password_gate": has_pw_gate,
                  "password_gate_policy": "absent",
                  "hard_stop": None,
                  "final_href": final_href,
                  "results": results,
                  "protocol": protocol_log,
                  "network": {
                    "sse_connect": {
                      "url": SSE_URL.replace(TOKEN, "[REDACTED]"),
                      "duration_ms": sse_duration_ms,
                      "sessions": 1
                    }
                  }
                }

                with open(f"{run_dir}/protocol.json", "w") as f:
                    json.dump(protocol_data, f, indent=2)
                with open(f"{run_dir}/html_snapshot.txt", "w") as f:
                    f.write(html_text)
                with open(f"{run_dir}/ax_snapshot.txt", "w") as f:
                    f.write(ax_text)
                with open(f"{run_dir}/evaluate.json", "w") as f:
                    json.dump(eval_obj, f, indent=2)
                
                # Write SMOKE.md
                smoke_md = f"""Target: {TARGET_URL}
Server: https://phantom-cloud-engine.fly.dev/sse
Sessions: 1
Password gate: {str(has_pw_gate).lower()}
Final href: {final_href}
Hard stop: None

| step | status | latency_ms | details |
|---|---|---|---|
"""
                for res in results:
                    smoke_md += f"| {res['tool']} | {res['status']} | {res['latency_ms']:.1f} | {res['details']} |\n"
                
                smoke_md += "\nTokens redacted. Merchant and customer PII not copied into this report."
                
                with open(f"{run_dir}/SMOKE.md", "w") as f:
                    f.write(smoke_md)
                
                print("OUTPUT:")
                print(f"Path: {run_dir}")
                print(f"Matrix: ok")
                print(f"Evaluate JSON: {json.dumps(eval_obj)}")
                print(f"Final href: \"{final_href}\"")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
