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
    
    evaluate_log = []
    
    step_num = 1
    def log_step(tool, params, status, result):
        nonlocal step_num
        step_num += 1

    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                log_step("tools/list", {}, "ok", "navigate, get_snapshot, click, type, evaluate, wait")
                
                # Step 2
                res = await session.call_tool("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard"})
                log_step("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard"}, "ok", res.content[0].text)
                
                # Step 3
                res = await session.call_tool("wait", {"delay_ms": 2000})
                log_step("wait", {"delay_ms": 2000}, "ok", res.content[0].text)
                
                # Step 4
                res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot1 = res.content[0].text
                log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot1)}")
                
                with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                    f.write("--- SNAPSHOT 1 ---\n" + snapshot1 + "\n\n")
                    
                # Step 5 - click Decline if present
                m = re.search(r"\[(e\d+):\s+(?:BUTTON|A|INPUT)[^\]]*?Decline[^\]]*?\]", snapshot1, re.I)
                if m:
                    ref = m.group(1)
                    res = await session.call_tool("click", {"ref": ref})
                    log_step("click", {"ref": ref}, "ok", res.content[0].text)
                    res = await session.call_tool("wait", {"delay_ms": 1000})
                    log_step("wait", {"delay_ms": 1000}, "ok", res.content[0].text)
                    
                    # Step 6
                    res = await session.call_tool("get_snapshot", {"mode": "html"})
                    snapshot2 = res.content[0].text
                    log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot2)}")
                    with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                        f.write("--- SNAPSHOT 2 ---\n" + snapshot2 + "\n\n")
                
                # Step 7
                expr1 = "JSON.stringify({href:location.href,title:document.title,price:(document.body.innerText.match(/\\$[0-9]+\\.[0-9]{2}/)||[])[0]||null,stock:/sold out|out of stock|in stock|esaurito|disponibile/i.test(document.body.innerText),text:document.body.innerText.replace(/\\s+/g,' ').slice(0,500)})"
                res = await session.call_tool("evaluate", {"expression": expr1})
                val1 = res.content[0].text
                log_step("evaluate", {"expression": "..."[:30]}, "ok", val1)
                evaluate_log.append({"url": "the-hidden-snowboard", "result": val1})
                
                # Step 8
                res = await session.call_tool("navigate", {"url": "https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard"})
                log_step("navigate", {"url": ".../the-archived-snowboard"}, "ok", res.content[0].text)
                
                # Step 9
                res = await session.call_tool("wait", {"delay_ms": 2000})
                log_step("wait", {"delay_ms": 2000}, "ok", res.content[0].text)
                
                # Step 10
                res = await session.call_tool("get_snapshot", {"mode": "html"})
                snapshot3 = res.content[0].text
                log_step("get_snapshot", {"mode": "html"}, "ok", f"len={len(snapshot3)}")
                with open(f"{out_dir}/html_snapshot.txt", "a") as f:
                    f.write("--- SNAPSHOT 3 ---\n" + snapshot3 + "\n\n")
                
                # Step 11
                expr2 = "JSON.stringify({href:location.href,title:document.title,price:(document.body.innerText.match(/\\$[0-9]+\\.[0-9]{2}/)||[])[0]||null,stock:/sold out|out of stock|in stock|esaurito|disponibile/i.test(document.body.innerText),text:document.body.innerText.replace(/\\s+/g,' ').slice(0,500)})"
                res = await session.call_tool("evaluate", {"expression": expr2})
                val2 = res.content[0].text
                log_step("evaluate", {"expression": "..."[:30]}, "ok", val2)
                evaluate_log.append({"url": "the-archived-snowboard", "result": val2})
                
                with open(f"{out_dir}/evaluate.json", "w") as f: json.dump(evaluate_log, f, indent=2)
                print(json.dumps({"path": out_dir, "evaluations": evaluate_log}))
                
    except Exception as e:
        print("Error:", str(e))

asyncio.run(run())
