import os
import sys
import time
import asyncio
import datetime
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "D2aZuYtdGL6tUfuV2egoxp"
SSE_URL = f"https://phantom-cloud-engine.fly.dev/sse/?token={TOKEN}"
TARGET_URL = "https://xxxxxx-r48zg9i1.myshopify.com/password"

async def main():
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{timestamp}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to {SSE_URL}")
    try:
        async with sse_client(SSE_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Session initialized.")
                
                # 1. navigate
                print(f"Navigating to {TARGET_URL}")
                await session.call_tool("navigate", {"url": TARGET_URL})
                
                # 2. wait 2000
                print("Waiting 2000ms")
                await session.call_tool("wait", {"delay_ms": 2000})
                
                # 3. get_snapshot html
                print("Getting HTML snapshot")
                html_res = await session.call_tool("get_snapshot", {"mode": "html"})
                html_text = html_res.content[0].text if html_res.content else ""
                html_lower = html_text.lower()
                
                # Check for captcha
                if "just a moment..." in html_lower or "challenge" in html_lower or "captcha" in html_lower:
                    with open(os.path.join(run_dir, "STOP.txt"), "w") as f:
                        f.write("Cloudflare or captcha\n")
                    print("Cloudflare/captcha detected. Stopped.")
                    return
                
                # 4. Evaluates
                evals = {
                    "E1": 'document.location.href + " | " + document.title',
                    "E2": 'JSON.stringify(Object.keys(window).filter(k => /product|collection|variant|price|inventory|password|shop|store/i.test(k)))',
                    "E3": 'JSON.stringify(performance.getEntriesByType("resource").map(r => r.name).filter(n => /product|collection|json|js/i.test(n)).slice(0,30))',
                    "E4": 'Array.from(document.scripts).map(s => s.src || s.textContent.slice(0,200)).join("\\n---\\n")',
                    "E5": 'document.documentElement.innerHTML.includes("niablu") || document.documentElement.innerHTML.match(/password["\']?\\s*[:=]\\s*["\'][^"\']{3,}/i) !== null',
                    "E6": 'fetch("/products.json").then(r=>r.status+" "+r.headers.get("content-type")).catch(e=>e.toString())',
                    "E7": 'fetch("/collections.json").then(r=>r.status+" "+r.headers.get("content-type")).catch(e=>e.toString())',
                    "E8": 'fetch("/products/beanie.js").then(r=>r.status).catch(e=>e.toString())',
                    "E9": 'fetch("/products/black-sunnies.js").then(r=>r.status).catch(e=>e.toString())',
                    "E10": 'JSON.stringify([...document.querySelectorAll("input,meta,script")].map(el => ({tag:el.tagName, name:el.name||el.id, value:(el.value||el.content||"").slice(0,100)})))'
                }
                
                results = {}
                for key, expr in evals.items():
                    print(f"Running {key}...")
                    res = await session.call_tool("evaluate", {"expression": expr})
                    results[key] = res.content[0].text if res.content else ""
                
                # Analyze for POTENTIAL_LEAK
                leak_keywords = ["beanie", "niablu", "black-sunnies"]
                is_leak = False
                for k, v in results.items():
                    val = str(v).lower()
                    if any(keyword in val for keyword in leak_keywords):
                        is_leak = True
                    if k in ["E6", "E7", "E8", "E9"] and "200 application/json" in val:
                        is_leak = True
                    if k == "E5" and "true" in val:
                        is_leak = True
                
                status = "POTENTIAL_LEAK" if is_leak else "CLEAN"
                
                note_content = f"Status: {status}\n\nResults:\n"
                for k, v in results.items():
                    note_content += f"{k}: {v}\n\n"
                    
                with open(os.path.join(run_dir, "evaluate_results.txt"), "w") as f:
                    f.write(note_content)
                print(f"Done. Wrote results to {run_dir}/evaluate_results.txt")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
