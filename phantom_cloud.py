import os
import asyncio
import json
import time
import hashlib
from urllib.parse import unquote, quote
from html.parser import HTMLParser
from contextlib import asynccontextmanager
import anyio
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import nodriver as uc
import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types as types

PORT = int(os.getenv("PORT", 8000))
UNKEY_API_ID = os.getenv("UNKEY_API_ID")
UNKEY_ROOT_KEY = os.getenv("UNKEY_ROOT_KEY")

# Concurrency guard: max one active browser session at a time (reversible)
_browser_lock = asyncio.Lock()
_active_sessions = 0
MAX_CONCURRENT_SESSIONS = 1

class StealthState:
    browser = None
    page = None
    element_map = {}

state = StealthState()

def _token_hash(token: str) -> str:
    if not token:
        return "none"
    return hashlib.sha256(token.encode()).hexdigest()[:12]

def _log(event: str, **kwargs):
    """Structured JSON log to stdout (visible via fly logs)."""
    payload = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **kwargs}
    print(json.dumps(payload, ensure_ascii=False), flush=True)

class AOMDistiller(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ignore_block = False
        self.text_buffer = []
        self.elements = {}
        self.e_counter = 1
        
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'svg', 'meta', 'noscript', 'canvas', 'link']:
            self.in_ignore_block = True
            return
        attr_dict = dict(attrs)
        if tag in ['a', 'button', 'input']:
            ref_id = f"e{self.e_counter}"
            self.e_counter += 1
            context = attr_dict.get('placeholder') or attr_dict.get('name') or attr_dict.get('aria-label') or attr_dict.get('id', 'unnamed')
            selector = f"#{attr_dict.get('id')}" if attr_dict.get('id') else None
            self.elements[ref_id] = {"tag": tag.upper(), "context": context, "selector": selector}
            self.text_buffer.append(f"[{ref_id}: {tag.upper()} '{context}']")
            
    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'svg', 'meta', 'noscript', 'canvas', 'link']:
            self.in_ignore_block = False
            
    def handle_data(self, data):
        if not self.in_ignore_block and data.strip():
            self.text_buffer.append(data.strip())

async def init_browser():
    if not state.browser:
        # Stealth args + software WebGL (SwiftShader/ANGLE) for container environments without GPU
        browser_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            # WebGL software path (B)
            "--use-gl=angle",
            "--use-angle=swiftshader-webgl",
            "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist",
            "--enable-webgl",
        ]
        state.browser = await uc.start(
            headless=False,
            sandbox=False,
            browser_executable_path="/usr/bin/google-chrome-stable",
            browser_args=browser_args
        )
        state.page = await state.browser.get("about:blank")
        _log("browser_started", headless=False, webgl_flags=True, chrome="google-chrome-stable")

server = Server("Phantom-Cloud")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="navigate",
            description="Naviga verso l'URL bypassando i WAF.",
            inputSchema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
        ),
        types.Tool(
            name="get_snapshot",
            description="Genera l'AOM Snapshot testuale della pagina.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    global _active_sessions
    start = time.monotonic()
    acquired = False
    try:
        # Concurrency guard: only block overlapping navigate calls; always release
        if name == "navigate":
            async with _browser_lock:
                if _active_sessions >= MAX_CONCURRENT_SESSIONS:
                    _log("tool_rejected", tool=name, reason="max_concurrent_sessions")
                    return [types.TextContent(type="text", text="Errore: limite sessioni concorrenti raggiunto. Riprova tra poco.")]
                _active_sessions += 1
                acquired = True
                
        if name == "navigate":
            await init_browser()
            await state.page.get(arguments["url"])
            await asyncio.sleep(4.5)
            duration_ms = int((time.monotonic() - start) * 1000)
            _log("tool_ok", tool="navigate", url=arguments.get("url", ""), duration_ms=duration_ms)
            return [types.TextContent(type="text", text=f"Navigazione completata su {arguments['url']}")]
            
        elif name == "get_snapshot":
            if not state.page:
                _log("tool_error", tool="get_snapshot", error="no_page")
                return [types.TextContent(type="text", text="Errore: Esegui prima il tool navigate.")]
            html = await state.page.get_content()
            parser = AOMDistiller()
            parser.feed(html)
            state.element_map = parser.elements
            dist = ' '.join(parser.text_buffer)[:8000]
            duration_ms = int((time.monotonic() - start) * 1000)
            _log("tool_ok", tool="get_snapshot", duration_ms=duration_ms, snapshot_len=len(dist))
            return [types.TextContent(type="text", text=f"--- AOM SNAPSHOT ---\n\n{dist}\n\n--- END SNAPSHOT ---")]
            
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        _log("tool_error", tool=name, error=str(e), duration_ms=duration_ms)
        return [types.TextContent(type="text", text=f"Errore critico: {str(e)}")]
    finally:
        if acquired:
            async with _browser_lock:
                _active_sessions = max(0, _active_sessions - 1)
                
    raise ValueError(f"Strumento non riconosciuto: {name}")

# --- INJECTED UNKEY LOGIC & ASGI NETWORKING ---
async def verify_unkey_token(token: str) -> bool:
    if not token:
        _log("unkey_fail", reason="empty_token")
        return False

    # Fallback when root key is not configured (local / emergency)
    if not UNKEY_ROOT_KEY:
        _log("unkey_warn", reason="missing_root_key_using_fallback")
        return token.startswith("ph_live_")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.unkey.com/v2/keys.verifyKey",
                headers={"Authorization": f"Bearer {UNKEY_ROOT_KEY}"},
                json={"key": token},
                timeout=3.0
            )
            if resp.status_code == 200:
                body = resp.json()
                data = body.get("data") or {}
                valid = bool(data.get("valid", False))
                if not valid:
                    _log("unkey_rejected", code=data.get("code"))
                else:
                    _log("unkey_accepted", token_hash=_token_hash(token), key_id=data.get("keyId"))
                return valid
            else:
                _log("unkey_error", status_code=resp.status_code, text=resp.text[:200])
                return False
    except Exception as e:
        _log("unkey_exception", error=str(e))
        return False

sse_transports = {}

async def _run_mcp_with_discover_guard(read_stream, write_stream):
    """mcp 1.0.0 crashes on pre-init methods (server/discover). Answer -32601 and keep the SSE session."""
    send_filtered, recv_filtered = anyio.create_memory_object_stream(0)

    async def pump():
        async with send_filtered:
            async for msg in read_stream:
                if isinstance(msg, Exception):
                    await send_filtered.send(msg)
                    continue
                root = getattr(msg, "root", msg)
                method = getattr(root, "method", None)
                msg_id = getattr(root, "id", None)
                if method == "server/discover":
                    _log("mcp_discover_ignored", msg_id=str(msg_id) if msg_id is not None else None)
                    error_msg = types.JSONRPCMessage.model_validate(
                        {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {"code": -32601, "message": "Method not found"},
                        }
                    )
                    await write_stream.send(error_msg)
                    continue
                await send_filtered.send(msg)

    async with anyio.create_task_group() as tg:
        tg.start_soon(pump)
        try:
            await server.run(recv_filtered, write_stream, server.create_initialization_options())
        finally:
            tg.cancel_scope.cancel()

async def sse_asgi(scope, receive, send):
    if scope["type"] == "http":
        request = Request(scope, receive)
        token = request.query_params.get("token", "")
        
        if not await verify_unkey_token(token):
            _log("auth_fail_sse", token_hash=_token_hash(token))
            response = JSONResponse({"error": "Unauthorized. Invalid Unkey token."}, status_code=401)
            await response(scope, receive, send)
            return
            
        _log("sse_connect", token_hash=_token_hash(token))
        # Path segment, not query string: Inspector encodes "?" into the path and 404s.
        transport = SseServerTransport(f"/messages/t/{quote(token, safe='')}")
        sse_transports[token] = transport
        
        try:
            async with transport.connect_sse(scope, receive, send) as streams:
                await _run_mcp_with_discover_guard(streams[0], streams[1])
        except Exception as e:
            _log("sse_stream_error", error=str(e), error_type=type(e).__name__)
        finally:
            sse_transports.pop(token, None)
            _log("sse_disconnect", token_hash=_token_hash(token))

async def messages_asgi(scope, receive, send):
    if scope["type"] == "http":
        request = Request(scope, receive)
        token = request.query_params.get("token", "")
        # Preferred: /messages/t/<token>?session_id=...
        # Fallbacks: encoded "?token=" variants from older endpoint forms
        if not token:
            candidates = [
                unquote(request.url.path),
                unquote(scope.get("path", "") or ""),
            ]
            raw_path = scope.get("raw_path")
            if isinstance(raw_path, (bytes, bytearray)):
                candidates.append(unquote(raw_path.decode("latin-1")))
            for raw in candidates:
                if not raw:
                    continue
                parts = [p for p in raw.split("/") if p]
                if "t" in parts:
                    i = parts.index("t")
                    if i + 1 < len(parts):
                        token = unquote(parts[i + 1])
                        break
                if "token=" in raw:
                    token = raw.split("token=", 1)[-1].split("&")[0].split("?")[0].strip()
                    if token:
                        break
            if token:
                _log("token_recovered_from_path", token_hash=_token_hash(token))
            else:
                _log("token_missing", path=unquote(request.url.path), scope_path=scope.get("path"))
        
        if not await verify_unkey_token(token):
            _log("auth_fail_msg", token_hash=_token_hash(token))
            response = JSONResponse({"error": "Unauthorized."}, status_code=401)
            await response(scope, receive, send)
            return
            
        transport = sse_transports.get(token)
        if not transport:
            _log("auth_fail", reason="no_active_transport_for_token")
            response = JSONResponse({"error": "No active SSE session."}, status_code=400)
            await response(scope, receive, send)
            return
            
        await transport.handle_post_message(scope, receive, send)

async def health_check(request: Request):
    """Readiness probe: reports whether browser process is initialized."""
    browser_ready = state.browser is not None and state.page is not None
    payload = {
        "status": "Phantom Cloud Online",
        "browser_ready": browser_ready,
        "active_sessions": _active_sessions,
    }
    status_code = 200 if True else 503
    return JSONResponse(payload, status_code=status_code)

@asynccontextmanager
async def lifespan(app):
    _log("service_start", port=PORT)
    yield
    if state.browser:
        try:
            state.browser.stop()
            _log("browser_stopped")
        except Exception as e:
            _log("browser_stop_error", error=str(e))

app = Starlette(
    routes=[
        Mount("/sse", app=sse_asgi),
        Mount("/sse/", app=sse_asgi),
        Mount("/messages", app=messages_asgi),
        Mount("/messages/", app=messages_asgi),
        Route("/", endpoint=health_check)
    ],
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
    ],
    lifespan=lifespan
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
