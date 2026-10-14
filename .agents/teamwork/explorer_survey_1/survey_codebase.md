# Phantom Cloud Codebase & Execution Architecture Survey Report

**Author**: `explorer_survey_1` (Codebase & Architecture Surveyor)  
**Date**: 2026-10-14  
**Working Directory**: `/Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy`  
**Target Tenants**: `funk-it-up-sdzgxmea` (Store A) & `xxxxxx-r48zg9i1` (Store B)  
**Research Handle**: `palabong@wearehackerone.com`  
**Core Codebase Preservation Status**: **100% Intact / Zero Modifications** (`phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`)

---

## 1. Executive Summary & Codebase Inventory

### 1.1 Scope & Core Codebase Preservation
In strict adherence to the project constraints and platform integrity policies, zero modifications were made to the core engine files:
- `phantom_cloud.py` (48,766 bytes, 1,125 lines) — **Unmodified**
- `Dockerfile` (1,146 bytes, 34 lines) — **Unmodified**
- `fly.toml` (584 bytes, 28 lines) — **Unmodified**
- `requirements.txt` (72 bytes, 7 lines) — **Unmodified**

All investigation was conducted in read-only mode across the repository files, runtime test harnesses, historical execution logs, and architectural archives.

### 1.2 Core Technology Stack: Architectural Clarification
While high-level specifications frequently anticipate a standard "FastAPI + Playwright" architecture, comprehensive code inspection reveals that Phantom Cloud was deliberately engineered on an alternate, highly specialized foundation designed specifically for deep stealth, low-level browser devtools control, and lightweight asynchronous Model Context Protocol (MCP) streaming:

| Dimension | Anticipated / Assumed | Actual Implementation in `phantom_cloud.py` | Rationale & Forensic Justification |
| :--- | :--- | :--- | :--- |
| **Web / ASGI Framework** | FastAPI | **Starlette ASGI** (`starlette.applications.Starlette`, `Route`, `Mount`, `Request`, `JSONResponse`) | Minimizes framework overhead and serialization latency; enables direct raw ASGI mounting (`sse_asgi`, `messages_asgi`) for native Server-Sent Events without Pydantic validation bottlenecks. |
| **Browser Automation Engine** | Playwright | **`nodriver`** (v0.30+, `import nodriver as uc`, the async successor to `undetected-chromedriver`) | Connects directly to Google Chrome via Chrome DevTools Protocol (CDP) WebSocket without injecting automated driver binaries (like `chromedriver`, `geckodriver`, or Playwright driver shims). Eliminates automated browser flags at the binary protocol level. |
| **Browser Binary** | Chromium / Playwright Browser Bundle | **Official Google Chrome Stable** (`google-chrome-stable` .deb) | Standard consumer Chrome binary ensures genuine browser signature, codec support (H.264), and official Google distribution hash. |
| **Protocol Specification** | Custom REST API | **Model Context Protocol (MCP)** v1.0.0 (`mcp.server.Server`) | Standards-compliant tool provider for AI agents and LLM execution environments. Exposes 6 core tools: `navigate`, `get_snapshot`, `click`, `type`, `evaluate`, `wait`. |
| **Streaming Transport** | WebSocket / SSE | **MCP SSE Transport** (`mcp.server.sse.SseServerTransport`) | Bidirectional asynchronous channel: `GET /sse/?token=<token>` creates persistent event stream; `POST /messages/t/<token>` accepts JSON-RPC calls. |
| **Virtual Display** | Headless Chrome flag | **Xvfb virtual frame buffer** (`-screen 0 1920x1080x24`) with `headless=False` | Chrome runs with `headless=False` inside an X11 virtual display buffer. This bypasses the distinct headless Chrome rendering pipeline entirely. |

### 1.3 Repository Inventory Breakdown

```
phantom_cloud_feasibility_strategy/
├── phantom_cloud.py               # Core MCP server, stealth injection, proxy CDP auth, ASGI routing
├── Dockerfile                     # Python 3.11-slim + Google Chrome stable + Xvfb container
├── fly.toml                       # Fly.io deployment config: 1 shared CPU, 1GB RAM, single-machine affinity
├── requirements.txt               # nodriver>=0.30, mcp==1.0.0, starlette, uvicorn, sse-starlette, httpx
├── README.md                      # Production surface, tool descriptions, local setup & cold-start notes
├── H1_5_SYNTHESIS.md              # 2026-10-12 synthesis of Staff UI vs GraphQL test runs on Store B
├── staff_test_results.json        # Test output demonstrating Cloudflare Turnstile interception on Store A admin
├── result.txt                     # Execution state marker: "H1-2 no contradiction"
├── tests/                         # Comprehensive pytest & verification suite (16 files)
│   ├── test_interaction_tools.py # Unit tests for click, type, evaluate, wait, resolve_element
│   ├── test_ax_snapshot.py       # Native Chrome Accessibility Tree (AX) vs HTML AOM tests
│   ├── test_bot_evasion.py       # Sannysoft navigation and snapshot verification
│   ├── run_cold_start_test.py    # Cold-start timing and lifecycle test harness
│   └── run_production_smoke.py   # Production 6-tool smoke verification script
├── grok/                          # Operational memory, architectures, and execution doctrine
│   ├── phantom_cloud_architecture.md # Authoritative end-to-end architecture & proxy deep dive
│   ├── project_memory             # Canonical L1 state memory & run history
│   ├── h1/                        # Shopify bug bounty roadmap, allowlists, and evidence notes
│   │   ├── H1_SHOPIFY_ROADMAP_20261007.md  # Track definitions, allowlists, and execution boundaries
│   │   ├── H1_6_STORE_B_PATH_20261007.md  # Store B testing path and evaluation criteria
│   │   └── evidence/             # 10 timestamped execution evidence notes (A1_H1_6_*)
│   └── archive/                   # Archived test prompts, consult reports, and Sannysoft smoke runs
├── commercial/                    # Rules of Engagement (RoE), Pilot offers, and pricing frames
└── [Execution Scripts]            # 25+ standalone test runners (run_h1_5_matrix.py, run_h1_6_store_b.py, etc.)
```

---

## 2. Phantom Cloud System Architecture Deep Dive

### 2.1 ASGI Server & Networking Architecture
The application entrypoint is an asynchronous Starlette application defined in `phantom_cloud.py` (lines 1101–1120) served via `uvicorn` on port 8000.

#### Route Map & Request Handling
1. **Probe Trapping Routes (`Route`)**:
   - `/.well-known/oauth-authorization-server`
   - `/.well-known/oauth-authorization-server/sse`
   - `/.well-known/openid-configuration`
   - `/.well-known/openid-configuration/sse`
   - `/sse/.well-known/openid-configuration`
   - `/json/version`
   *Mechanism*: When LLM client platforms or IDE extensions (e.g. Cursor, MCP Inspector) connect to `/sse`, they probe for OAuth/OIDC auto-discovery. If the server answers with HTTP 401 Unauthorized, client IDEs display modal login popups and hang. The handler `oauth_probe_not_found()` returns HTTP 404 (`{"error": "not_found"}`), signaling that OAuth is not configured and allowing standard token fallback.
2. **SSE Streaming Sub-app (`Mount("/sse", app=sse_asgi)`)**:
   - Accepts `GET /sse/?token=<token>` (HTTP 405 on non-GET; HTTP 204 on OPTIONS).
   - Validates the token against the authentication layer.
   - Creates or retrieves an existing `SseServerTransport` instance from the in-memory dictionary `sse_transports[token]`.
   - Advertises the client POST message endpoint as `/messages/t/<token>`.
   - Wraps the session runner in `_run_mcp_with_discover_guard()`.
3. **JSON-RPC Command Sub-app (`Mount("/messages", app=messages_asgi)`)**:
   - Accepts `POST /messages/t/<token>?session_id=<id>`.
   - Extracts the token from the URL path segment `/t/<token>` (with defensive regex fallbacks for older encoded URL variants).
   - Routes the POST body into `transport.handle_post_message(scope, receive, send)`.
4. **Health Check & Diagnostics (`Route("/", endpoint=health_check)`, `Route("/debug_chrome", endpoint=debug_chrome)`)**:
   - `/` returns JSON: `{"status": "Phantom Cloud Online", "browser_ready": bool, "active_sessions": int}`.
   - `/debug_chrome` executes `/usr/bin/google-chrome-stable` as a test subprocess and captures stdout/stderr to diagnose X11 display errors.

#### `server/discover` Guard (`_run_mcp_with_discover_guard`)
The official MCP SDK (version 1.0.0) terminates SSE connections when encountering pre-initialization methods introduced in newer specifications (such as `server/discover` from the 2026-07-28 probe spec). Phantom Cloud installs an in-memory stream interceptor (`anyio.create_memory_object_stream`):
```python
if method == "server/discover":
    error_msg = types.JSONRPCMessage.model_validate({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": "Method not found"}
    })
    await write_stream.send(error_msg)
    continue
```
This intercepts the probe, answers with standard JSON-RPC `-32601` (Method Not Found), and preserves the underlying SSE stream.

### 2.2 Authentication Architecture & Unkey v2
Authentication is handled centrally by `verify_unkey_token(token: str)` (lines 857–892):
- **Production Mode**: When the environment variable `UNKEY_ROOT_KEY` (starts with `unkey_`) is configured, Phantom Cloud invokes the Unkey v2 API (`POST https://api.unkey.com/v2/keys.verifyKey`) with a 3.0-second timeout. If valid, the connection is authorized and logged with a SHA-256 token hash prefix (`_token_hash()`).
- **Local / Fallback Mode**: When `UNKEY_ROOT_KEY` is not set (e.g. during local debugging or tests), the server falls back to allowing any token starting with the prefix `ph_live_` (e.g., `ph_live_local_verify`, `ph_live_D2aZuYtdGL6tUfuV2egoxp`).

### 2.3 Browser Lifecycle & CDP Connection Management
Browser orchestration is implemented in `init_browser()` (lines 346–484).

#### Startup Modes
1. **Existing Chrome Attachment (Local Debugging Mode)**:
   If `CHROME_DEBUGGING_PORT` is set in the environment:
   ```python
   config = uc.Config()
   config.host = "127.0.0.1"
   config.port = int(cdp_port)
   state.browser = await uc.start(config=config)
   ```
   The engine attaches to an existing running Chrome instance (e.g., a local desktop browser running on macOS with pre-authenticated sessions). It inspects existing tabs, targets any Shopify tab, enables the CDP Page domain, and injects the stealth payload.
2. **Fresh Chrome Spawning (Container / Standalone Mode)**:
   - **Process Sanitization**: Executes `pkill -9 -f chrome` and `pkill -9 -f chromium` to eliminate zombie processes.
   - **Flag Configuration**:
     - Automation removal: `--no-sandbox`, `--disable-blink-features=AutomationControlled`, `--disable-dev-shm-usage`.
     - Window geometry: `--window-size=1920,1080`.
     - Container software WebGL: `--use-gl=angle`, `--use-angle=swiftshader-webgl`, `--enable-unsafe-swiftshader`, `--ignore-gpu-blocklist`, `--enable-webgl`.
     - Proxy injection: `--proxy-server=<host:port>` (if proxy is configured and alive).
   - **Extended Connection Monkey-Patch (`patch_nodriver`)**:
     Default `nodriver` attempts to connect to Chrome's debugging port for only 2.5 seconds (5 attempts). On resource-constrained VMs (e.g. Fly.io shared-cpu-1x), cold starts routinely took 4–7 seconds, causing intermittent startup failures. `phantom_cloud.py` monkey-patches `nodriver.core.browser.Browser.start` to poll 30 times (15.0 seconds total), ensuring 100% startup reliability.
   - **3-Attempt Exponential Retry Loop**: If browser startup fails, any partial processes are killed and startup is retried up to 3 times before raising `RuntimeError`.

#### Target Swap Auto-Recovery
In modern web applications (particularly multi-tenant OAuth and Shopify Polaris Admin), navigations across origins trigger Chrome Cross-Origin Isolation (process swaps). When a process swap occurs, the CDP WebSocket target disconnects. In `handle_call_tool`:
```python
if state.browser and getattr(state, "page", None):
    try:
        await state.page.send(uc.cdp.runtime.evaluate(expression="1"))
    except Exception:
        await state.browser.update_targets()
        if state.browser.tabs:
            state.page = state.browser.main_tab
            await state.page.send(uc.cdp.page.enable())
            await state.page.send(uc.cdp.page.add_script_to_evaluate_on_new_document(source=STEALTH_INJECTION_PAYLOAD))
            await _arm_proxy_fetch()
```
The engine detects disconnected targets, re-syncs tabs with `browser.update_targets()`, re-binds `state.page`, re-injects the stealth script on the new target document, and re-arms the proxy fetch handlers.

### 2.4 Stealth Mechanisms & Evasion Layers

Phantom Cloud implements a defense-in-depth stealth pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chrome Binary & Flags                        │
│  - google-chrome-stable official distribution                   │
│  - headless=False inside Xvfb (:99)                             │
│  - --disable-blink-features=AutomationControlled                │
│  - --use-gl=angle --use-angle=swiftshader-webgl                 │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│       CDP Page.addScriptToEvaluateOnNewDocument                 │
│                 (STEALTH_INJECTION_PAYLOAD)                     │
│                                                                 │
│  1. Native Function Cloaking:                                   │
│     Function.prototype.toString wrapped via WeakMap             │
│     All patched functions return "function <name>() { [native code] }"
│                                                                 │
│  2. Webdriver Removal:                                          │
│     delete Navigator.prototype.webdriver                        │
│     delete navigator.webdriver                                  │
│                                                                 │
│  3. Hardware Entropy Spoofing:                                  │
│     navigator.hardwareConcurrency = 8                           │
│     navigator.deviceMemory = 8                                  │
│                                                                 │
│  4. Dialog Auto-Resolution:                                     │
│     window.alert() -> true; window.confirm() -> true            │
│     window.prompt() -> null                                     │
│                                                                 │
│  5. WebGL Parameter Virtualization:                             │
│     UNMASKED_VENDOR_WEBGL = "Google Inc. (NVIDIA)"              │
│     UNMASKED_RENDERER_WEBGL = "ANGLE (NVIDIA, NVIDIA GeForce    │
│       RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"                │
│                                                                 │
│  6. Deterministic Canvas Noise:                                 │
│     CanvasRenderingContext2D.prototype.getImageData patched    │
│     Applies ±1 pseudo-random noise derived from SESSION_SEED   │
└─────────────────────────────────────────────────────────────────┘
```

#### Accessibility Object Model (AOM) Distillation
Rather than returning raw, token-heavy HTML to AI agents, `phantom_cloud.py` provides two distinct snapshot modes:
1. **HTML Mode (`AOMDistiller`, default)**:
   - Built on Python's native `HTMLParser`.
   - Strips non-visual / non-interactive tags (`script`, `style`, `svg`, `meta`, `noscript`, `canvas`, `link`).
   - Assigns stable semantic references: `[e1: A 'unnamed']`, `[e2: INPUT 'password']`, `[e3: BUTTON 'Enter']`.
   - Caches mappings in `state.element_map` for reference-based `click` and `type` tool calls.
2. **AX Mode (`mode="ax"`)**:
   - Queries native Chrome Accessibility Tree via CDP (`Accessibility.getFullAXTree`).
   - Filters out `node.ignored` elements.
   - Maps backend DOM node IDs (`backend_dom_node_id`) to stable references (`ax1`, `ax2`, etc.).
   - During resolution, uses CDP `DOM.resolveNode` and `Runtime.callFunctionOn` to tag the target node in the live DOM.

### 2.5 Proxy Handling Architecture
The proxy subsystem (`phantom_cloud.py`, lines 286–345, 393–441) manages authenticated outbound routing:

1. **Environment Configuration**: Checks `RESIDENTIAL_PROXY_SERVER` or fallback alias `PHANTOM_PROXY_URL` (format: `http://user:pass@host:port`).
2. **Two-Stage Credential Decoupling**: Chrome's CLI flag `--proxy-server` does not accept embedded HTTP basic credentials (`user:pass@host`). Embedding credentials triggers Chrome startup errors or leaks authentication tokens in process tables (`ps aux`). Phantom Cloud parses the proxy URL:
   - Netloc without credentials (`http://host:port`) is appended to `--proxy-server`.
   - Username and password are saved in `state.proxy_username` and `state.proxy_password`.
3. **Synchronous 2.5s Pre-Flight Probe**: Before launching Chrome with the proxy flag, Phantom Cloud issues an HTTP GET against `http://example.com/` using `httpx.Client(proxy=...)` with a 2.5-second timeout. If the proxy fails (due to bad credentials, expired credit, or latency), the engine logs `proxy_fallback_to_direct_connection` and launches Chrome directly.
4. **Transparent CDP Authentication (`_arm_proxy_fetch`)**:
   When the proxy requires authentication, Chrome encounters HTTP 407 (Proxy Authentication Required). Phantom Cloud handles this by enabling the CDP `Fetch` domain with `handle_auth_requests=True`:
   ```python
   async def handle_auth_required(event: uc.cdp.fetch.AuthRequired):
       challenge_response = uc.cdp.fetch.AuthChallengeResponse(
           response="ProvideCredentials",
           username=state.proxy_username,
           password=state.proxy_password
       )
       await state.page.send(
           uc.cdp.fetch.continue_with_auth(
               request_id=event.request_id,
               auth_challenge_response=challenge_response
           )
       )
   ```
   This automatically injects credentials without opening browser dialogs.

### 2.6 Fly.io Deployment Configuration
The production engine is configured in `fly.toml`:
- **App**: `phantom-cloud-engine`
- **Primary Region**: `fra` (Frankfurt, Germany)
- **VM Sizing**: `shared-cpu-1x`, 1 GB RAM
- **Port Mapping**: Internal port 8000 mapped to HTTPS (port 443) with `force_https = true`
- **Concurrency**: Soft limit 20, Hard limit 25 connections
- **Machine Affinity**: `min_machines_running = 1`, scaled to **exactly 1 machine** (`78197e2be34d78`).

#### Critical Architecture Constraint: The Single-Machine Requirement
The `SseServerTransport` session objects and Chrome browser process instances reside strictly in **process memory**. Fly.io's global load balancer routes incoming requests across active machines. If the app were scaled to 2 or more machines:
- An AI client opening an SSE connection (`GET /sse/?token=...`) would land on Machine A.
- A subsequent command (`POST /messages/t/...`) might land on Machine B.
- Machine B would inspect its local `sse_transports` dictionary, find no active transport, and return HTTP 400 (`{"error": "No active SSE session"}`).
Scaling to exactly 1 machine guarantees 100% session affinity and eliminates cold starts.

---

## 3. Execution Dynamics: Cloudflare Turnstile on Fly.io vs. Local SSE Runner

A primary objective of this investigation is explaining why Cloudflare Turnstile blocks occur on Fly.io while the Local SSE runner (`http://127.0.0.1:8000`) succeeds.

### 3.1 Comparative Architectural Assessment

| Vector / Dimension | Fly.io Cloud Engine (`phantom-cloud-engine.fly.dev`) | Local SSE Runner (`http://127.0.0.1:8000`) | Direct Impact on Cloudflare Turnstile Detection |
| :--- | :--- | :--- | :--- |
| **IP Transit & ASN Reputation** | Egress from Fly.io Datacenter IP range (`AS398606`, Frankfurt `fra`). When residential proxy is disabled/expired, IP is categorized as Commercial Datacenter / Cloud Hosting. | Egress from researcher's local residential ISP or home network. Pristine consumer IP reputation score. | **CRITICAL**: Cloudflare evaluates IP threat score before evaluating browser headers. Datacenter IPs are placed on the highest risk tier, triggering mandatory interactive Turnstile challenges (`Just a moment...` / `Ci siamo quasi...`). |
| **GPU / WebGL Emulation** | CPU-based software rasterizer: Google Chrome runs `--use-angle=swiftshader-webgl` and `--enable-unsafe-swiftshader` inside Docker. | Real physical GPU (e.g. Apple Silicon M-series or discrete NVIDIA/AMD GPU) with native hardware acceleration. | **CRITICAL**: Deep WebGL inspection tests shader compilation micro-benchmarks, floating-point precision tolerances, and extension sets. SwiftShader reveals software rasterization signatures regardless of high-level string spoofing. Codebase explicitly acknowledges: *"SwiftShader NOT claimed solved"*. |
| **Cross-Entropy Incoherence** | WebGL renderer string is spoofed to: `ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)`. The User-Agent is: `Mozilla/5.0 (X11; Linux x86_64) ... Chrome/155.0.0.0`. | Consistent native environment: macOS UA (`Macintosh; Intel Mac OS X 10_15_7` or Apple Silicon) paired with native Metal/OpenGL renderer. | **HIGH**: An unmasked renderer claiming Microsoft DirectX (`Direct3D11`) on a Linux platform (`X11; Linux x86_64`) is an impossible cross-entropy signal. Anti-bot heuristics flag this mismatch immediately as synthetic spoofing. |
| **Canvas Hash & Tampering** | Applies deterministic pseudo-random noise (`SESSION_SEED`) by monkey-patching `CanvasRenderingContext2D.prototype.getImageData`. | Native canvas rendering: Font antialiasing, subpixel layout, and text shaping reflect genuine macOS CoreGraphics engine. | **HIGH**: Turnstile generates hidden canvas drawing operations and inspects prototype integrity via `Object.getOwnPropertyDescriptor`. Tampered or noisy `getImageData` triggers bot anomaly detection. |
| **Display & System Peripherals** | Headless container using Xvfb: Screen resolution fixed at `1920x1080x24`. `navigator.mediaDevices.enumerateDevices()` returns **0** audio/video devices. Battery API static (`charging: true, level: 1`). | Native desktop display: Retina pixel ratio (`devicePixelRatio = 2`), authentic display scaling, genuine microphones, webcams, speakers, and dynamic battery telemetry. | **MEDIUM**: Anti-bot challenge payloads evaluate client environment completeness. Zero media devices in conjunction with a datacenter IP strongly correlates with containerized scrapers. |
| **Browser Execution Context** | Standalone containerized browser with synthetic CDP mouse events (`element.mouse_click()`). | Ability to attach via `CHROME_DEBUGGING_PORT` to an authentic user profile already logged into Shopify with valid session cookies. | **CRITICAL**: Attaching to a live authenticated browser inherits authenticated session tokens (`_shopify_s`, `_shopify_y`), pre-cleared Turnstile clearance tokens (`cf_clearance`), and genuine human telemetry. |
| **Operational Guardrail / Rule** | Strict rule: **DO NOT CLICK TURNSTILE / HCAPTCHA**. When Turnstile appears, automated runners execute a `HARD_STOP`. | Interactive resolution or pre-authenticated session eliminates Turnstile appearance altogether. | **PROCEDURAL**: On Fly.io, the appearance of Turnstile is fatal because project doctrine forbids automated clicking of challenges. Locally, Turnstile is bypassed natively. |

### 3.2 Forensic Breakdown: Why `accounts.shopify.com` Blocks Fly.io
When Phantom Cloud on Fly.io navigates to `https://accounts.shopify.com/login` or `https://admin.shopify.com/store/funk-it-up-sdzgxmea`:
1. Cloudflare's Edge receives the TCP connection and TLS ClientHello from Fly.io's IP range.
2. The IP is flagged as a hosting provider (Datacenter ASN).
3. Cloudflare serves the Turnstile challenge HTML containing encrypted obfuscated JavaScript telemetry collectors.
4. The collector gathers:
   - WebGL renderer strings vs. platform OS (Direct3D11 vs. Linux x86_64 mismatch).
   - Canvas pixel hashing (detects noise injection on `getImageData`).
   - Hardware peripheral count (0 media devices).
5. The combined telemetry score categorizes the client as an automated bot.
6. The page remains locked on title `Just a moment...` (or Italian localized `Ci siamo quasi…`).
7. Phantom Cloud's polling loop in `navigate` times out or records `isDeniedUI = true` / `challenge = true`, stopping execution.

---

## 4. Forensic Audit of Prior Run Artifacts, Logs, and Historical Evidence

A deep-dive survey was conducted across repository artifacts, historical evaluation runs, and evidence logs.

### 4.1 Track H1-5 Evidence: UI State vs. GraphQL Access (`H1_5_SYNTHESIS.md`)
On 2026-10-12, an extensive evaluation matrix was executed targeting Store B (`xxxxxx-r48zg9i1`) using the staff session `palabong+staff@wearehackerone.com`:

| Tested Resource | UI State | Admin GraphQL Query Attempted | GraphQL Result | Vulnerability Finding Candidate? |
| :--- | :--- | :--- | :--- | :--- |
| **Orders** (`/orders`) | **Denied** (Permission banner) | `query{orders(first:1){edges{node{id name}}}}` | `{"error": "Failed to fetch"}` | **None** (UI Denied / API Error) |
| **Settings** (`/settings`) | **Allowed** (Settings custom data) | `query{shop{id name email}}` | `{"error": "Failed to fetch"}` | **None** (UI Allowed / API Error) |
| **Payments** (`/settings/payments`) | **Denied** (Permission banner) | `query{shop{paymentSettings{supportedDigitalWallets}}}` | `{"errors": "[API] Invalid API key or access token..."}` | **None** (UI Denied / API Error) |
| **Themes** (`/themes`) | **Allowed** (Theme library controls) | `query{themes(first:5){edges{node{id name}}}}` | `{"errors": "[API] Invalid API key or access token..."}` | **None** (UI Allowed / API Error) |

#### Critical Forensic Discovery on Track H1-5
In `run_orders_eval.py` and `run_payments_eval.py`, the evaluate expression was written as:
```javascript
return await fetch('https://xxxxxx-r48zg9i1.myshopify.com/admin/api/2024-10/graphql.json', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: '...'})
})
```
**Why this query failed**:
1. **Cross-Origin / Header Boundary**: The browser was navigated to `https://admin.shopify.com/store/xxxxxx-r48zg9i1/orders` (the `admin.shopify.com` origin). Calling `fetch()` to `https://xxxxxx-r48zg9i1.myshopify.com` constitutes a cross-origin request.
2. **Missing Access Token vs. Internal Web Session**: The endpoint `/admin/api/2024-10/graphql.json` is Shopify's Public Admin API, requiring an app token in the `X-Shopify-Access-Token` header. When called without this header, Shopify correctly responds:
   `[API] Invalid API key or access token (unrecognized login or wrong password)`.
3. **The Genuine Internal Polaris Endpoint**: Shopify's web admin UI does not use `/admin/api/.../graphql.json` with API keys; it utilizes internal batching GraphQL endpoints (e.g., `https://admin.shopify.com/api/shopify/2024-10/graphql.json` or `/store/<store>/graphql`) authenticated via internal Polaris session tokens and CSRF headers.
*Conclusion for R1 Strategy*: Future H1-5 test procedures must extract authenticated Polaris web session headers and CSRF tokens from the local page context, or target the internal web GraphQL endpoint.

### 4.2 Track H1-6 Evidence: Storefront Primitives Closure (`run_h1_6_store_b.py`, `evidence/`)
Historical notes in `grok/h1/evidence/` provide conclusive evidence regarding storefront pricing, sold-out items, and hidden variants:

1. **Store A (`funk-it-up-sdzgxmea`) Observations**:
   - Products tested: "The Hidden Snowboard" (`variant 50535758364858`) and "The Archived Snowboard" (`variant 50535758266554`).
   - On the Product Display Pages (PDP), prices were displayed ($749.95 and $629.95).
   - When the Add to Cart button was clicked via MCP (`click ref=e48`), the DOM click succeeded, but upon navigating to `/cart`, **the cart remained completely empty** (`subtotal $0.00 USD`).
   - *Forensic Verdict*: Shopify's backend cart engine dropped unorderable, archived, and unpublished items server-side. Public pricing display on a test theme is cosmetic and does not move money.
2. **Store B (`xxxxxx-r48zg9i1`) Observations**:
   - Products tested: `beanie` (variant `67407288565988`) and `black-sunnies` (variant `67407280242916`).
   - Admin status verified via `run_h1_6_store_b.py`: Both items were marked `Active`, published to the Online Store channel, with sellable stock.
   - Reference run `prod_postdeploy_20261007T192921Z` showed `/cart/add.js` returning HTTP 200 with total $300.00 USD.
   - *Forensic Verdict*: Legitimate intended sales behavior. No contradiction between admin intent and storefront availability.
   - **Track H1-6 is officially CLOSED**.

### 4.3 Track H1-7 Evidence: Cross-Shop Multi-Tenant Isolation / IDOR (`run_h1_7_matrix.py`)
In `run_h1_7_matrix.py`, test matrices evaluated whether Store A credentials could interact with Store B objects:
- Store B cart add requesting Store A variant `50535758364858`: Returned **HTTP 422 Unprocessable Entity** (`"Cannot find variant"`).
- Store B storefront querying Store A product `.js` API (`/products/the-hidden-snowboard.js`): Returned **HTTP 404 Not Found**.
- Staff A accessing Store B Admin routes (`https://admin.shopify.com/store/xxxxxx-r48zg9i1`): Redirected to login or permission denial.
- Zero cross-tenant data leakage was observed across tested storefront primitives.

### 4.4 Turnstile Interception Evidence (`staff_test_results.json`)
The file `staff_test_results.json` captures direct evidence of Cloudflare Turnstile intercepting admin navigations:
```json
{
  "home": {
    "href": "https://admin.shopify.com/store/funk-it-up-sdzgxmea",
    "title": "Ci siamo quasi…",
    "denied": true,
    "bodyPreview": "È necessario verificare la tua connessione prima di procedere"
  },
  "settings": { ... "title": "Ci siamo quasi…", ... },
  "themes": { ... "title": "Ci siamo quasi…", ... }
}
```
This confirms that without proper session clearance or residential IP transit, admin navigations trigger the Turnstile challenge screen, preventing automated assessment.

---

## 5. Architectural Recommendations for Subsequent Phases

Based on this comprehensive survey, the following architectural and operational strategies are recommended for the Phase 1 decomposition and subsequent track deliverables:

### 5.1 Dual-Engine Execution Topology
To resolve the Turnstile bottleneck while maximizing automation reliability:
1. **Local SSE Runner (`http://127.0.0.1:8000`) for Authenticated Tracks (H1-5, H1-7 Admin)**:
   - Run Phantom Cloud locally on macOS, launched with `CHROME_DEBUGGING_PORT`.
   - The researcher logs in once via a regular desktop Chrome profile (residential IP, native GPU, pre-authenticated Polaris session).
   - Phantom Cloud attaches to this existing Chrome session.
   - Cloudflare Turnstile does not trigger; all Polaris admin endpoints, internal GraphQL endpoints, and session cookies are accessible.
2. **Fly.io Cloud Engine (`phantom-cloud-engine.fly.dev`) for Storefront & Unauthenticated Scans**:
   - Utilize Fly.io for public storefront primitives, collection queries, and catalog crawling where Turnstile is not enforced.
   - Ensure `RESIDENTIAL_PROXY_SERVER` is configured if testing sensitive storefront forms.

### 5.2 Corrected Internal GraphQL Extraction Model for Track H1-5
To prevent false-positive "Invalid API key" errors, the H1-5 test harness must execute within the Polaris web admin origin and capture native session tokens:
```javascript
// Step 1: Capture Polaris CSRF and session headers from the authenticated page context
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') 
               || window.__st?.csrf 
               || window.shopify?.csrf;

// Step 2: Query the internal web Admin GraphQL endpoint with session cookies included
const res = await fetch('/api/shopify/2024-10/graphql.json', {
    method: 'POST',
    credentials: 'include',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify({ query: 'query { orders(first: 1) { edges { node { id name } } } }' })
});
return await res.json();
```

### 5.3 Formal Closure Dossier for Track H1-6
Document formal closure criteria based on verified observations:
- Server-side cart drop confirmed: Archived and unpublished items fail to persist in `/cart`.
- Test data theme display does not constitute a vulnerability.
- Redirect testing effort from H1-6 into high-impact Tracks H1-5 and H1-7.

---

## 6. Survey Verification & Compliance Checklist

- [x] `phantom_cloud.py` hash and contents 100% verified and preserved (no changes).
- [x] `Dockerfile`, `fly.toml`, and `requirements.txt` 100% verified and preserved (no changes).
- [x] Full Starlette ASGI + `nodriver` architecture mapped and analyzed.
- [x] Cloudflare Turnstile failure dynamics on Fly.io documented and contrasted with Local SSE runner.
- [x] Prior run artifacts (`H1_5_SYNTHESIS.md`, `staff_test_results.json`, `grok/h1/evidence/`) cataloged.
- [x] Scope strictly limited to self-owned stores (`funk-it-up-sdzgxmea` & `xxxxxx-r48zg9i1`).
- [x] Written report compiled to `.agents/teamwork/explorer_survey_1/survey_codebase.md`.
