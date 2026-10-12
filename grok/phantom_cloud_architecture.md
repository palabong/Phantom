# Phantom Cloud — Proxy & E2E Architecture

PROJECT: phantom_cloud
UPDATED: 2026-09-25T18:47Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-25T18:47Z

## What It Is

Phantom Cloud is a **remote, stealth-browsing MCP server**. AI agents connect to it over SSE, issue MCP tool calls (`navigate`, `click`, `get_snapshot`, etc.), and the server drives a real Chrome instance behind WAF-evasion stealth layers. It is deployed as a single stateful Fly.io machine in Frankfurt.

---

## End-to-End Request Lifecycle

```mermaid
sequenceDiagram
    participant Agent as AI Agent / MCP Client
    participant FlyEdge as Fly.io Edge (HTTPS)
    participant Uvicorn as Uvicorn (port 8000)
    participant Starlette as Starlette Router
    participant SSE as SseServerTransport
    participant MCP as MCP Server ("Phantom-Cloud")
    participant Chrome as Chrome (nodriver)
    participant Proxy as Residential Proxy (optional)
    participant Target as Target Website

    Agent->>FlyEdge: GET /sse/?token=<key>
    FlyEdge->>Uvicorn: forward (internal :8000)
    Uvicorn->>Starlette: Mount /sse → sse_asgi
    Starlette->>Starlette: verify_unkey_token(token)
    Note over Starlette: Unkey v2 API call or ph_live_ prefix fallback
    Starlette->>SSE: transport.connect_sse() → opens SSE stream
    SSE-->>Agent: SSE connection established (event stream)
    Note over SSE,Agent: Client now knows /messages/t/<token> endpoint

    Agent->>FlyEdge: POST /messages/t/<token> (JSON-RPC: initialize)
    FlyEdge->>Uvicorn: forward
    Uvicorn->>Starlette: Mount /messages → messages_asgi
    Starlette->>Starlette: extract token from path segment /t/<token>
    Starlette->>Starlette: verify_unkey_token(token)
    Starlette->>SSE: transport.handle_post_message()
    SSE->>MCP: JSON-RPC → server.run()

    Agent->>FlyEdge: POST /messages/t/<token> (call_tool: navigate)
    FlyEdge->>Starlette: (same auth + dispatch)
    MCP->>MCP: init_browser() [first call only]
    Note over MCP,Chrome: pkill orphans → uc.start(stealth args) → inject JS
    MCP->>Chrome: page.get(url)
    Chrome->>Proxy: HTTP CONNECT (if RESIDENTIAL_PROXY_SERVER set)
    Note over Chrome,Proxy: CDP Fetch.AuthRequired → auto-supply credentials
    Proxy->>Target: GET url (residential IP)
    Target-->>Chrome: HTML response
    MCP-->>Agent: SSE event: "Navigazione completata"

    Agent->>FlyEdge: POST /messages/t/<token> (call_tool: get_snapshot)
    MCP->>Chrome: page.get_content() or CDP Accessibility.getFullAXTree
    Chrome-->>MCP: raw HTML / AX nodes
    MCP->>MCP: AOMDistiller (html) or AX node mapping
    MCP-->>Agent: SSE event: AOM/AX snapshot text
```

---

## Proxy Setup — Deep Dive

The proxy layer is entirely in [init_browser()](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L264-L411) and runs **once** on the first `navigate` call.

### 1. Environment Variables

| Var | Purpose |
|-----|---------|
| `RESIDENTIAL_PROXY_SERVER` | Primary. Full proxy URL, e.g. `http://user:pass@gate.provider.com:7777` |
| `PHANTOM_PROXY_URL` | Fallback alias (same format) |

Either variable is parsed at [L291](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L291). If neither is set, Chrome connects directly — no proxy at all.

### 2. URL Parsing & Credential Extraction

```python
# L298-312
parsed = urlparse(proxy_server)          # split scheme://user:pass@host:port
proxy_username = parsed.username          # extracted for CDP auth later
proxy_password = parsed.password
cleaned_netloc = parsed.hostname          # host without creds
if parsed.port:
    cleaned_netloc += f":{parsed.port}"
chrome_proxy_val = f"{scheme}://{cleaned_netloc}"  # cred-free URL for Chrome flag
```

> [!IMPORTANT]
> Chrome's `--proxy-server` flag **cannot contain embedded credentials** (`user:pass@host`). Credentials must be supplied separately via CDP. This two-stage design is the reason the code splits the URL.

### 3. Pre-flight Health Check

Before trusting the proxy, a **synchronous 2.5 s httpx probe** hits `http://example.com/` through the full proxy URL (with credentials):

```python
# L322-326
with httpx.Client(proxy=formatted_proxy, timeout=2.5) as client:
    resp = client.get("http://example.com/")
    if resp.status_code in (200, 301, 302, 404):
        use_proxy = True  # proxy is alive
```

If the probe fails (timeout, auth error, DNS failure), `use_proxy` stays `False` and Chrome falls back to a **direct connection** with a log entry `proxy_fallback_to_direct_connection`. This is a resilience mechanism — the server never hard-fails on a dead proxy.

### 4. Chrome Launch with `--proxy-server`

When `use_proxy` is `True`:

```python
# L333
browser_args.append(f"--proxy-server={chrome_proxy_val}")
```

This tells Chrome to route **all HTTP/HTTPS traffic** through the proxy. The value is credential-free (e.g. `http://gate.provider.com:7777`).

### 5. CDP Fetch Domain — Automatic Credential Supply

Chrome will hit a `407 Proxy Authentication Required` on the first request. The code handles this transparently via the **CDP Fetch domain**:

```python
# L377-409
await state.page.send(uc.cdp.fetch.enable(handle_auth_requests=True))
```

Two CDP event handlers are registered:

| CDP Event | Handler | What it does |
|-----------|---------|-------------|
| `Fetch.RequestPaused` | [handle_request_paused](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L379-L385) | Continues every intercepted request (passthrough) |
| `Fetch.AuthRequired` | [handle_auth_required](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L387-L403) | Responds with `ProvideCredentials` + username/password extracted at step 2 |

```mermaid
sequenceDiagram
    participant Chrome
    participant CDPFetch as CDP Fetch Domain
    participant Proxy as Proxy Server
    participant Handler as AuthRequired Handler

    Chrome->>Proxy: CONNECT target.com:443
    Proxy-->>Chrome: 407 Proxy Auth Required
    Chrome->>CDPFetch: Fetch.AuthRequired event
    CDPFetch->>Handler: event dispatched
    Handler->>CDPFetch: continueWithAuth(ProvideCredentials, user, pass)
    CDPFetch->>Chrome: retry with Proxy-Authorization header
    Chrome->>Proxy: CONNECT target.com:443 (authenticated)
    Proxy-->>Chrome: 200 Connection Established
    Chrome->>Proxy: GET https://target.com/page
    Proxy->>Target: forward
    Target-->>Chrome: response
```

> [!TIP]
> This pattern works for **any HTTP(S) proxy that uses 407 challenges** — residential rotating proxies, datacenter proxies, SOCKS-to-HTTP bridges, etc. The credentials are never embedded in Chrome flags or page-visible state.

---

## Stealth Layers

The proxy is just the network layer. On top of it, the browser is hardened against bot detection:

| Layer | Where | What |
|-------|-------|------|
| `--disable-blink-features=AutomationControlled` | Chrome flag | Removes `navigator.webdriver = true` |
| `STEALTH_INJECTION_PAYLOAD` | [L105-216](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L105-L216) — CDP `Page.addScriptToEvaluateOnNewDocument` | Removes webdriver property, spoofs hardware concurrency/device memory, virtualizes WebGL params (RTX 3080), applies deterministic canvas noise, auto-dismisses dialogs |
| `Function.prototype.toString` cloak | Inside payload | Makes all patched functions return `[native code]` |
| Software WebGL (SwiftShader) | Chrome flags `--use-angle=swiftshader-webgl` | Provides consistent WebGL fingerprint in headless containers |
| `nodriver` (undetected-chromedriver successor) | Runtime | Avoids Selenium CDP leaks entirely |

---

## Auth Layer (SSE + Messages)

### Connection Phase

1. Client → `GET /sse/?token=<key>` → [sse_asgi](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L837-L870)
2. Token verified against **Unkey v2** API (or `ph_live_` prefix fallback if `UNKEY_ROOT_KEY` is unset)
3. An `SseServerTransport` is created (or reused) per token and stored in the [sse_transports](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L802) dict
4. The SSE stream stays open — client receives JSON-RPC responses as SSE events

### Command Phase

1. Client → `POST /messages/t/<token>` with JSON-RPC body → [messages_asgi](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L872-L917)
2. Token is extracted from the **path segment** (`/t/<token>`), not query string — this avoids MCP Inspector URL-encoding bugs
3. The matching `SseServerTransport` is looked up and `handle_post_message()` dispatches into the MCP server

### server/discover Guard

MCP Inspector sends a `server/discover` probe (spec 2026-07-28) before `initialize`. The MCP SDK v1.0.0 crashes on unknown pre-init methods. The [_run_mcp_with_discover_guard](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py#L804-L835) wrapper intercepts this, replies with JSON-RPC error `-32601` (Method not found), and keeps the SSE session alive.

---

## Infrastructure — Fly.io Deployment

```
┌─────────────────────────────────────────────────┐
│  Fly.io Edge (phantom-cloud-engine.fly.dev)     │
│  HTTPS termination · region: fra                │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  VM: shared-cpu-1x · 1 GB RAM            │  │
│  │  min_machines_running = 1 (always warm)   │  │
│  │                                           │  │
│  │  ┌─────────┐     ┌──────────────────┐    │  │
│  │  │  Xvfb   │────▶│  Chrome Stable   │    │  │
│  │  │ :99     │     │  (nodriver)       │    │  │
│  │  └─────────┘     └────────┬─────────┘    │  │
│  │                           │              │  │
│  │  ┌────────────────────────┴──────────┐   │  │
│  │  │  Uvicorn :8000                    │   │  │
│  │  │  ├── /sse/     → SSE stream       │   │  │
│  │  │  ├── /messages/→ JSON-RPC POST    │   │  │
│  │  │  ├── /         → health check     │   │  │
│  │  │  └── /debug_chrome → diagnostics  │   │  │
│  │  └───────────────────────────────────┘   │  │
│  └───────────────────────────────────────────┘  │
│  Concurrency: hard=25 connections, soft=20      │
│  Scaled to exactly 1 machine (session affinity) │
└─────────────────────────────────────────────────┘
         │
         │ --proxy-server (if configured)
         ▼
┌─────────────────────┐
│  Residential Proxy  │
│  (rotating IPs)     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Target Website     │
│  (WAF-protected)    │
└─────────────────────┘
```

### Why Exactly 1 Machine?

The `SseServerTransport` instances and the Chrome browser `state` object live **in-process memory**. There is no external session store. If Fly.io routed SSE `GET` and JSON-RPC `POST` to different machines, the `POST` would find no matching transport and 400. Pinning to 1 machine with `min_machines_running = 1` guarantees affinity and eliminates cold starts.

---

## Key Files

| File | Role |
|------|------|
| [phantom_cloud.py](file:///Users/daniele_palagi/Desktop/phantom_cloud/phantom_cloud.py) | Entire server: stealth, proxy, MCP tools, ASGI routing, auth |
| [Dockerfile](file:///Users/daniele_palagi/Desktop/phantom_cloud/Dockerfile) | Container: Python 3.11 + Chrome Stable + Xvfb |
| [fly.toml](file:///Users/daniele_palagi/Desktop/phantom_cloud/fly.toml) | Fly.io deployment: region, concurrency, VM size |
| [.env.example](file:///Users/daniele_palagi/Desktop/phantom_cloud/.env.example) | Env var template (PORT, UNKEY_ROOT_KEY) |
| [requirements.txt](file:///Users/daniele_palagi/Desktop/phantom_cloud/requirements.txt) | Python deps: nodriver, mcp, starlette, uvicorn, httpx |
