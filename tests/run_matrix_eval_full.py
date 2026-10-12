import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from mcp import ClientSession
from mcp.client.sse import sse_client

PROD_HOST = "https://phantom-cloud-engine.fly.dev"
TARGET_URL = "https://bot.sannysoft.com/"
EXPECTED_TOOLS = ["navigate", "get_snapshot", "click", "type", "evaluate", "wait"]
CONNECT_TIMEOUT = 120
SSE_READ_TIMEOUT = 300
SESSION_READ_TIMEOUT = timedelta(seconds=180)
REF_RE = re.compile(r"\[(e\d+):\s*([A-Z]+)")

def resolve_token():
    env = os.getenv("PHANTOM_AUTH_TOKEN", "").strip()
    if env:
        return env
    return "D2aZuYtdGL6tUfuV2egoxp"

TOKEN = resolve_token()
SSE_URL = f"{PROD_HOST}/sse/?token={TOKEN}"

def masked_url():
    if not TOKEN:
        return f"{PROD_HOST}/sse/?token="
    if len(TOKEN) <= 8:
        return f"{PROD_HOST}/sse/?token=REDACTED"
    return f"{PROD_HOST}/sse/?token={TOKEN[:3]}...{TOKEN[-4:]}"

def redact(text):
    if not text or not TOKEN:
        return text
    return text.replace(TOKEN, "REDACTED")

def snapshot_refs(snapshot):
    return REF_RE.findall(snapshot or "")

async def call(session, tool_name, kwargs):
    print(f"\n[EXEC] Tool: {tool_name} | Args: {kwargs}")
    t0 = time.perf_counter()
    try:
        res = await session.call_tool(tool_name, kwargs)
        dt = time.perf_counter() - t0
        text = res.content[0].text if res.content else ""
        is_error = bool(res.isError) or text.startswith("Errore")
        status = "ERROR" if is_error else "SUCCESS"
        print(f"  -> {status} | Latency: {dt*1000:.1f}ms | Payload Length: {len(text)}")
        return text, is_error
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"  -> EXCEPTION | Latency: {dt*1000:.1f}ms | {type(e).__name__}: {redact(str(e))}")
        return None, True

async def main():
    print(f"Connecting to production MCP at {masked_url()} ...")
    
    # Create run directory
    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path("runs") / f"matrix_eval_{utc_now}"
    run_dir.mkdir(parents=True, exist_ok=True)
    payloads_dir = run_dir / "payloads"
    payloads_dir.mkdir(exist_ok=True)
    
    protocol = []
    network = []
    
    with open(run_dir / "MATRIX.md", "w") as f:
        f.write("# Matrix Evaluation\n\nStarting run...\n")

    def log_protocol(action, details):
        protocol.append({"time": datetime.now(timezone.utc).isoformat(), "action": action, "details": details})

    async with sse_client(
        SSE_URL,
        headers={},
        timeout=CONNECT_TIMEOUT,
        sse_read_timeout=SSE_READ_TIMEOUT,
    ) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=SESSION_READ_TIMEOUT,
        ) as session:
            await session.initialize()
            print("Session established. Commencing Test Matrix...\n")
            log_protocol("initialize", "Session established")

            # 1. tools/list
            listed = await session.list_tools()
            names = [tool.name for tool in listed.tools]
            print(f"Tools: {names}")
            log_protocol("tools/list", {"tools": names})

            # 2. navigate then wait
            nav_text, _ = await call(session, "navigate", {"url": TARGET_URL})
            wait_text, _ = await call(session, "wait", {"delay_ms": 2000})
            
            # 3. get_snapshot html
            html_text, _ = await call(session, "get_snapshot", {"mode": "html"})
            if html_text:
                with open(run_dir / "html_snapshot.txt", "w") as f:
                    f.write(html_text)

            # Evaluate just in case evaluate.json is needed
            eval_text, _ = await call(session, "evaluate", {"expression": "JSON.stringify({href: location.href})"})
            if eval_text:
                with open(run_dir / "evaluate.json", "w") as f:
                    f.write(eval_text)

            # 4. Hit - click and type
            # Need fresh html snapshot before hit
            html_text2, _ = await call(session, "get_snapshot", {"mode": "html"})
            refs = snapshot_refs(html_text2)
            inputs = [ref for ref, role in refs if role in {"INPUT", "TEXTAREA"}]
            if inputs:
                type_text, _ = await call(session, "type", {"ref": inputs[0], "text": "PHANTOM-TRACE", "clear": True})
                with open(payloads_dir / "hit_type.txt", "w") as f:
                    f.write(type_text or "")
            
            if refs:
                click_ref = refs[0][0]
                # Avoid clicking the input we just typed in, if possible
                if len(refs) > 1 and inputs and click_ref == inputs[0]:
                    click_ref = refs[1][0]
                click_hit_text, _ = await call(session, "click", {"ref": click_ref})
                with open(payloads_dir / "hit_click.txt", "w") as f:
                    f.write(click_hit_text or "")

            # 5. Miss - click selector
            click_miss_text, _ = await call(session, "click", {"selector": "#phantom-missing-target"})
            with open(payloads_dir / "miss_click.txt", "w") as f:
                f.write(click_miss_text or "")
                
            # 6. ax last
            ax_text, _ = await call(session, "get_snapshot", {"mode": "ax"})
            if ax_text:
                with open(run_dir / "ax_snapshot.txt", "w") as f:
                    f.write(ax_text)
                    
            with open(run_dir / "protocol.json", "w") as f:
                json.dump(protocol, f, indent=2)
                
            with open(run_dir / "network.json", "w") as f:
                json.dump(network, f, indent=2)

            with open(run_dir / "ASSESSMENT.md", "w") as f:
                f.write(f"# Assessment\n\nRun complete.\n")
                
            print("\nMatrix Evaluation Complete. Directory created:", run_dir)

if __name__ == "__main__":
    asyncio.run(main())
