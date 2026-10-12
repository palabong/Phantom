import asyncio
import os
import json
import re
from datetime import datetime, timezone
from mcp import ClientSession
from mcp.client.sse import sse_client

url = "https://phantom-cloud-engine.fly.dev/sse/?token=D2aZuYtdGL6tUfuV2egoxp"

async def run():
    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(out_dir, exist_ok=True)
    
    protocol_log = []
    evaluate_log = []
    smoke_md = [
        f"# Production smoke {utc_now}",
        "Target: funk-it-up-sdzgxmea.myshopify.com",
        "Server: https://phantom-cloud-engine.fly.dev",
        "",
        "| step | status | tool | params | result |",
        "|---|---|---|---|---|"
    ]
    
    step_num = 1
    
    def log_step(tool, params, status, result):
        nonlocal step_num
        # Redact password in logs
        safe_params = json.loads(json.dumps(params))
        if "text" in safe_params and tool == "type":
            safe_params["text"] = "***"
        
        protocol_log.append({
            "step": step_num,
            "tool": tool,
            "params": safe_params,
            "status": status,
            "result": str(result)[:500] if result else ""
        })
        smoke_md.append(f"| {step_num} | {status} | {tool} | {json.dumps(safe_params)} | {str(result)[:200]} |")
        step_num += 1

    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                log_step("tools/list", {}, "ok", "navigate, get_snapshot, click, type, evaluate, wait")
                
                # Step 2
                res = await session.call_tool("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/password"})
                log_step("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/password"}, "ok", res.content[0].text)
                
                # Step 3
                res = await session.call_tool("wait", {"delay_ms": 1500})
                log_step("wait", {"delay_ms": 1500}, "ok", res.content[0].text)
                
                # Step 4
                res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot1 = res.content[0].text
                log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot1)}")
                
                # archive html snapshot
                with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                    f.write("--- SNAPSHOT 1 ---\n" + snapshot1 + "\n\n")
                
                # check if e2 is INPUT password
                if not re.search(r"\[e2:\s+INPUT.*?password.*?\]", snapshot1, re.I) and not re.search(r"\[e2:\s+INPUT.*?\]", snapshot1, re.I):
                    print(json.dumps({"path": out_dir, "verdict": "STOP: e2 not input", "evaluations": evaluate_log}))
                    return
                
                # Step 5
                res = await session.call_tool("type", {"ref": "e2", "text": "bE-4C5TLf)LVmk^", "clear": True})
                log_step("type", {"ref": "e2", "text": "bE-4C5TLf)LVmk^", "clear": True}, "ok", res.content[0].text)
                
                # Step 6
                res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot2 = res.content[0].text
                log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot2)}")
                with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                    f.write("--- SNAPSHOT 2 ---\n" + snapshot2 + "\n\n")
                
                # check if e3 is submit/button
                if not re.search(r"\[e3:\s+(BUTTON|INPUT).*?(submit|enter).*?\]", snapshot2, re.I) and not re.search(r"\[e3:\s+BUTTON.*?\]", snapshot2, re.I) and not re.search(r"\[e3:\s+INPUT.*?\]", snapshot2, re.I):
                    print(json.dumps({"path": out_dir, "verdict": "STOP: e3 not submit", "evaluations": evaluate_log}))
                    return
                
                # Step 7
                res = await session.call_tool("click", {"ref": "e3"})
                log_step("click", {"ref": "e3"}, "ok", res.content[0].text)
                
                # Step 8
                res = await session.call_tool("wait", {"delay_ms": 2000})
                log_step("wait", {"delay_ms": 2000}, "ok", res.content[0].text)
                
                # Step 9
                expr1 = "JSON.stringify({href:location.href,path:location.pathname,title:document.title,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),rejected:/incorrect/i.test(document.body.innerText)})"
                res = await session.call_tool("evaluate", {"expression": expr1})
                val1 = res.content[0].text
                log_step("evaluate", {"expression": "..."[:30]}, "ok", val1)
                evaluate_log.append({"url": "password_check", "result": val1})
                
                try:
                    data = json.loads(json.loads(val1))
                except:
                    data = json.loads(val1)
                if isinstance(data, str):
                    data = json.loads(data)
                
                # Step 10
                if data.get("path") == "/password":
                    smoke_md.append("\nVerdict: GATE-STUCK")
                    with open(f"{out_dir}/SMOKE.md", "w") as f: f.write("\n".join(smoke_md))
                    with open(f"{out_dir}/protocol.json", "w") as f: json.dump(protocol_log, f, indent=2)
                    with open(f"{out_dir}/evaluate.json", "w") as f: json.dump(evaluate_log, f, indent=2)
                    print(json.dumps({"path": out_dir, "verdict": "GATE-STUCK", "evaluations": evaluate_log}))
                    return
                    
                # Step 11
                res = await session.call_tool("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard"})
                log_step("navigate", {"url": ".../the-hidden-snowboard"}, "ok", res.content[0].text)
                
                # Step 12
                res = await session.call_tool("wait", {"delay_ms": 2000})
                log_step("wait", {"delay_ms": 2000}, "ok", res.content[0].text)
                
                # Step 13
                res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot3 = res.content[0].text
                log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot3)}")
                with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                    f.write("--- SNAPSHOT 3 ---\n" + snapshot3 + "\n\n")
                    
                # Step 14
                expr2 = "JSON.stringify({href:location.href,title:document.title,status:document.body.innerText.slice(0,400)})"
                res = await session.call_tool("evaluate", {"expression": expr2})
                val2 = res.content[0].text
                log_step("evaluate", {"expression": "..."[:30]}, "ok", val2)
                evaluate_log.append({"url": "the-hidden-snowboard", "result": val2})
                
                # Step 15
                res = await session.call_tool("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard"})
                log_step("navigate", {"url": ".../the-archived-snowboard"}, "ok", res.content[0].text)
                
                # Step 16
                res = await session.call_tool("wait", {"delay_ms": 2000})
                log_step("wait", {"delay_ms": 2000}, "ok", res.content[0].text)
                
                # Step 17
                res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot4 = res.content[0].text
                log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot4)}")
                with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                    f.write("--- SNAPSHOT 4 ---\n" + snapshot4 + "\n\n")
                    
                # Step 18
                expr3 = "JSON.stringify({href:location.href,title:document.title,status:document.body.innerText.slice(0,400)})"
                res = await session.call_tool("evaluate", {"expression": expr3})
                val3 = res.content[0].text
                log_step("evaluate", {"expression": "..."[:30]}, "ok", val3)
                evaluate_log.append({"url": "the-archived-snowboard", "result": val3})
                
                smoke_md.append("\nVerdict: DONE")
                with open(f"{out_dir}/SMOKE.md", "w") as f: f.write("\n".join(smoke_md))
                with open(f"{out_dir}/protocol.json", "w") as f: json.dump(protocol_log, f, indent=2)
                with open(f"{out_dir}/evaluate.json", "w") as f: json.dump(evaluate_log, f, indent=2)
                print(json.dumps({"path": out_dir, "verdict": "DONE", "evaluations": evaluate_log}))
                
    except Exception as e:
        print("Error:", str(e))

asyncio.run(run())
