import asyncio
import json
import os
import re
import sys
import time
from datetime import timedelta
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
    cfg_path = Path.home() / ".mcp-inspector" / "mcp.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        url = cfg.get("mcpServers", {}).get("phantom-cloud-engine", {}).get("url", "")
        token = (parse_qs(urlparse(url).query).get("token") or [""])[0].strip()
        if token:
            return token
    return ""


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
        if is_error:
            print(f"  -> Msg: {redact(text)}")
        return text, is_error
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"  -> EXCEPTION | Latency: {dt*1000:.1f}ms | {type(e).__name__}: {redact(str(e))}")
        return None, True


async def main():
    if not TOKEN:
        print("PHANTOM_AUTH_TOKEN is unset and ~/.mcp-inspector/mcp.json has no phantom-cloud-engine token.")
        sys.exit(1)

    print(f"Connecting to production MCP at {masked_url()} ...")
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

            print("==========================================================")
            print(" tools/list")
            print("==========================================================")
            t0 = time.perf_counter()
            listed = await session.list_tools()
            dt = (time.perf_counter() - t0) * 1000
            names = [tool.name for tool in listed.tools]
            missing = [name for name in EXPECTED_TOOLS if name not in names]
            extra = [name for name in names if name not in EXPECTED_TOOLS]
            set_ok = not missing and not extra and len(names) == 6
            status = "SUCCESS" if set_ok else "ERROR"
            print(f"\n[EXEC] tools/list | Args: {{}}")
            print(f"  -> {status} | Latency: {dt:.1f}ms | Payload Length: {len(names)}")
            print(f"  -> Tools: {', '.join(names)}")
            if missing:
                print(f"  -> Missing: {', '.join(missing)}")
            if extra:
                print(f"  -> Extra: {', '.join(extra)}")
            if set_ok and names != EXPECTED_TOOLS:
                print(f"  -> Order differs from production surface: {EXPECTED_TOOLS}")

            print("\n==========================================================")
            print(" PATTERN A (State Ingestion & Discovery)")
            print("==========================================================")
            await call(session, "navigate", {"url": TARGET_URL})
            await call(session, "wait", {"delay_ms": 500})
            snap1, _ = await call(session, "get_snapshot", {"mode": "html"})
            if snap1:
                print(f"  -> Truncated snippet: {snap1[:100]}...")
            await call(session, "get_snapshot", {"mode": "ax"})

            print("\n==========================================================")
            print(" PATTERN B (Viewport Manipulation)")
            print("==========================================================")
            await call(session, "evaluate", {"expression": "window.scrollBy(0, 600); 'scrolled_down'"})

            print("\n==========================================================")
            print(" PATTERN C (Targeted Interaction & Synchronization)")
            print("==========================================================")
            await call(
                session,
                "evaluate",
                {
                    "expression": "Array.from(document.querySelectorAll('th, td')).some(el => el.textContent.includes('Broken Image Dimensions'))"
                },
            )

            refs = snapshot_refs(snap1)
            inputs = [ref for ref, role in refs if role in {"INPUT", "TEXTAREA"}]
            if inputs:
                await call(session, "type", {"ref": inputs[0], "text": "PHANTOM-TRACE-9901", "clear": True})
            else:
                print("\n[EXEC] Tool: type | Args: N/A")
                print("  -> N/A | Latency: 0.0ms | html snapshot has no input")

            if refs:
                await call(session, "click", {"ref": refs[0][0]})
            else:
                print("\n[EXEC] Tool: click | Args: {'ref': None}")
                print("  -> ERROR | Latency: 0.0ms | no e* ref in html snapshot")

            print("\n==========================================================")
            print(" PATTERN D (State Modification & Full Recovery)")
            print("==========================================================")
            await call(session, "evaluate", {"expression": "window.scrollTo(0, 0); 'scrolled_top'"})
            await call(
                session,
                "evaluate",
                {
                    "expression": "JSON.stringify({title:document.title,href:location.href,webdriver:navigator.webdriver,ua:navigator.userAgent})"
                },
            )
            snap2, _ = await call(session, "get_snapshot", {"mode": "html"})
            if snap2:
                print(f"  -> Final Payload Verification Length: {len(snap2)} chars.")
            miss_text, miss_err = await call(session, "click", {"selector": "#phantom-missing-target"})
            if miss_text and re.search(r"non trovato|not found", miss_text, re.I):
                print("  -> Controlled not-found = PASS")
            elif miss_err:
                print("  -> Controlled not-found not confirmed")

            print("\nMatrix Evaluation Complete.")


if __name__ == "__main__":
    asyncio.run(main())
