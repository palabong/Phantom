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

def patch_nodriver():
    import nodriver.core.browser as browser_mod
    from nodriver.core.browser import HTTPApi
    from nodriver import ContraDict
    import nodriver.core.util as nodriver_util
    import pathlib
    import logging
    
    logger = logging.getLogger("nodriver.core.browser")
    is_posix = os.name == "posix"
    
    async def patched_start(self=None) -> browser_mod.Browser:
        if not self:
            raise RuntimeError("use ``await Browser.create()`` to create a new instance")
        if self._process or self._process_pid:
            if self._process.returncode is not None:
                return await self.create(config=self.config)
            raise RuntimeError("ignored! this call has no effect when already running.")
            
        connect_existing = False
        if self.config.host is not None and self.config.port is not None:
            connect_existing = True
        else:
            self.config.host = "127.0.0.1"
            self.config.port = nodriver_util.free_port()
            
        if not connect_existing:
            if not pathlib.Path(self.config.browser_executable_path).exists():
                raise FileNotFoundError("Could not find browser executable")
                
        if getattr(self.config, "_extensions", None):
            self.config.add_argument("--load-extension=%s" % ",".join(str(_) for _ in self.config._extensions))
            
        exe = self.config.browser_executable_path
        params = self.config()
        
        if not connect_existing:
            self._process = await asyncio.create_subprocess_exec(
                exe,
                *params,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                close_fds=is_posix,
            )
            self._process_pid = self._process.pid
            
        self._http = HTTPApi((self.config.host, self.config.port))
        nodriver_util.get_registered_instances().add(self)
        await asyncio.sleep(0.5)
        
        # We increase to 30 attempts (15 seconds total) to be extremely bulletproof for cold-starts!
        for attempt in range(30):
            try:
                self.info = ContraDict(await self._http.get("version"), silent=True)
            except Exception:
                if attempt == 29:
                    logger.debug("could not start", exc_info=True)
                await asyncio.sleep(0.5)
            else:
                break
                
        if not self.info:
            raise Exception("Failed to connect to browser. Connection timeout.")
            
        self.websocket_url = self.info.webSocketDebuggerUrl
        await self.attach()
        await self.update_targets()
        return self
        
    browser_mod.Browser.start = patched_start

patch_nodriver()

# Concurrency guard: max one active browser session at a time (reversible)
_browser_lock = asyncio.Lock()
_active_sessions = 0
MAX_CONCURRENT_SESSIONS = 1

STEALTH_INJECTION_PAYLOAD = """(() => {
    'use strict';

    // --- Native Function Cloaking ---
    const nativeToString = Function.prototype.toString;
    const patchedMap = new WeakMap();

    function wrapNative(fn, name, length = 0) {
        Object.defineProperty(fn, 'name', { value: name, configurable: true });
        Object.defineProperty(fn, 'length', { value: length, configurable: true });
        patchedMap.set(fn, `function ${name}() { [native code] }`);
        return fn;
    }

    const customToString = function toString() {
        if (patchedMap.has(this)) return patchedMap.get(this);
        return nativeToString.call(this);
    };
    wrapNative(customToString, 'toString', 0);
    Function.prototype.toString = customToString;

    // --- Fix 1: Eliminate FPScanner WEBDRIVER FAIL ---
    // Remove 'webdriver' from Navigator prototype chain completely
    try {
        if (Object.getPrototypeOf(navigator)) {
            delete Object.getPrototypeOf(navigator).webdriver;
        }
        delete navigator.webdriver;
    } catch (e) {}

    // --- Fix 2: Hardware Entropy Coherence (RTX 3080 Baseline) ---
    const defineGetter = (proto, prop, value) => {
        const getter = function() { return value; };
        wrapNative(getter, `get ${prop}`, 0);
        Object.defineProperty(proto, prop, {
            get: getter,
            enumerable: true,
            configurable: true
        });
    };

    defineGetter(Navigator.prototype, 'hardwareConcurrency', 8);
    defineGetter(Navigator.prototype, 'deviceMemory', 8);

    // --- Fix 3: Dialog Auto-Resolution (Bot Challenge Dialog Handler) ---
    window.alert = wrapNative(function alert() { return true; }, 'alert', 0);
    window.confirm = wrapNative(function confirm() { return true; }, 'confirm', 0);
    window.prompt = wrapNative(function prompt() { return null; }, 'prompt', 0);

    // --- Fix 4: WebGL Parameter Virtualization ---
    const UNMASKED_VENDOR_WEBGL = 37445;
    const UNMASKED_RENDERER_WEBGL = 37446;
    const TARGET_VENDOR = 'Google Inc. (NVIDIA)';
    const TARGET_RENDERER = 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)';

    function applyWebGLSpoof(proto) {
        if (!proto || !proto.getParameter) return;
        const origGetParam = proto.getParameter;
        const fakeGetParam = function getParameter(p) {
            if (p === UNMASKED_VENDOR_WEBGL) return TARGET_VENDOR;
            if (p === UNMASKED_RENDERER_WEBGL) return TARGET_RENDERER;
            if (p === 7936) return 'WebKit';
            if (p === 7937) return 'WebKit WebGL';
            return origGetParam.call(this, p);
        };
        wrapNative(fakeGetParam, 'getParameter', 1);
        Object.defineProperty(proto, 'getParameter', {
            value: fakeGetParam,
            writable: true,
            enumerable: false,
            configurable: true
        });
    }
    if (typeof WebGLRenderingContext !== 'undefined') applyWebGLSpoof(WebGLRenderingContext.prototype);
    if (typeof WebGL2RenderingContext !== 'undefined') applyWebGLSpoof(WebGL2RenderingContext.prototype);

    // --- Fix 5: Deterministic Canvas Noise ---
    const SESSION_SEED = Math.floor(Math.random() * 2147483647);
    function getNoise(index, seed) {
        let x = ((index ^ seed) >>> 0);
        x = Math.imul((x >>> 16) ^ x, 0x45d9f3b);
        x = Math.imul((x >>> 16) ^ x, 0x45d9f3b);
        x = ((x >>> 16) ^ x) >>> 0;
        return (x % 47 === 0) ? ((x % 2 === 0) ? 1 : -1) : 0;
    }

    if (typeof CanvasRenderingContext2D !== 'undefined') {
        const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        const fakeGetImageData = function getImageData(sx, sy, sw, sh) {
            const imgData = origGetImageData.apply(this, arguments);
            if (imgData && imgData.data) {
                for (let i = 0; i < imgData.data.length; i += 4) {
                    for (let c = 0; c < 3; c++) {
                        const n = getNoise(i + c, SESSION_SEED);
                        if (n !== 0) {
                            const val = imgData.data[i + c] + n;
                            imgData.data[i + c] = val < 0 ? 0 : (val > 255 ? 255 : val);
                        }
                    }
                }
            }
            return imgData;
        };
        wrapNative(fakeGetImageData, 'getImageData', 4);
        Object.defineProperty(CanvasRenderingContext2D.prototype, 'getImageData', {
            value: fakeGetImageData,
            writable: true,
            enumerable: false,
            configurable: true
        });
    }
})();"""

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
        # Pre-cleanup: Kill any previous orphaned chrome/chromium processes to prevent conflicts/resource exhaustion
        try:
            import subprocess
            subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
            subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
            _log("pre_start_cleanup_done")
        except Exception as e:
            _log("pre_start_cleanup_failed", error=str(e))

        # Stealth args + software WebGL (SwiftShader/ANGLE) for container environments without GPU
        browser_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--window-size=1920,1080",
            # WebGL software path (B)
            "--use-gl=angle",
            "--use-angle=swiftshader-webgl",
            "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist",
            "--enable-webgl",
        ]
        
        # Route outbound Chrome connections through a residential proxy pool.
        # Resolves RESIDENTIAL_PROXY_SERVER or PHANTOM_PROXY_URL environment variables.
        proxy_server = os.getenv("RESIDENTIAL_PROXY_SERVER") or os.getenv("PHANTOM_PROXY_URL")
        proxy_username = None
        proxy_password = None
        use_proxy = False
        chrome_proxy_val = None
        
        if proxy_server:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_server)
            if not parsed.scheme:
                parsed = urlparse(f"http://{proxy_server}")
                
            proxy_username = parsed.username
            proxy_password = parsed.password
            
            # Extract server address without embedded credentials for Chrome's --proxy-server flag
            cleaned_netloc = parsed.hostname
            if parsed.port:
                cleaned_netloc = f"{cleaned_netloc}:{parsed.port}"
                
            scheme = parsed.scheme or "http"
            chrome_proxy_val = f"{scheme}://{cleaned_netloc}"
            
            # Perform a fast pre-flight health check to ensure proxy credentials/routing are alive
            formatted_proxy = proxy_server
            if proxy_username and proxy_password:
                formatted_proxy = f"{scheme}://{proxy_username}:{proxy_password}@{cleaned_netloc}"
                
            _log("proxy_preflight_checking", proxy_server=chrome_proxy_val)
            try:
                # 2.5s quick timeout check against example.com
                with httpx.Client(proxy=formatted_proxy, timeout=2.5) as client:
                    resp = client.get("http://example.com/")
                    if resp.status_code in (200, 301, 302, 404): # standard proxy success responses
                        use_proxy = True
                        _log("proxy_preflight_passed", status_code=resp.status_code)
                    else:
                        _log("proxy_preflight_failed_status", status_code=resp.status_code)
            except Exception as pre_err:
                _log("proxy_preflight_failed_exception", error=str(pre_err))
                
            if use_proxy:
                browser_args.append(f"--proxy-server={chrome_proxy_val}")
                _log("proxy_configured", proxy_server=chrome_proxy_val, has_auth=bool(proxy_username))
            else:
                _log("proxy_fallback_to_direct_connection", reason="proxy_is_dead_or_unauthorized")
        
        last_err = None
        chrome_path = "/usr/bin/google-chrome-stable"
        if not os.path.exists(chrome_path):
            chrome_path = None # Let nodriver auto-detect on macOS / Windows
            
        for attempt in range(1, 4):
            try:
                _log("browser_start_attempt", attempt=attempt)
                state.browser = await uc.start(
                    headless=False,
                    sandbox=False,
                    browser_executable_path=chrome_path,
                    browser_args=browser_args
                )
                break
            except Exception as e:
                last_err = e
                _log("browser_start_failed", attempt=attempt, error=str(e))
                # Post-attempt cleanup: kill any half-started/failed chrome processes
                try:
                    import subprocess
                    subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
                    subprocess.run(["pkill", "-9", "-f", "chromium"], capture_output=True)
                except Exception:
                    pass
                if attempt < 3:
                    await asyncio.sleep(2.0 * attempt)
        else:
            raise RuntimeError(f"Failed to start browser after 3 attempts: {str(last_err)}")

        state.page = await state.browser.get("about:blank")
        
        # WebGL & MediaDevices CDP script injection
        await state.page.send(uc.cdp.page.enable())
        await state.page.send(uc.cdp.page.add_script_to_evaluate_on_new_document(source=STEALTH_INJECTION_PAYLOAD))
        
        # Enable CDP proxy credentials auto-supply if auth credentials are provided
        if use_proxy and proxy_username and proxy_password:
            try:
                await state.page.send(uc.cdp.fetch.enable(handle_auth_requests=True))
                
                async def handle_request_paused(event: uc.cdp.fetch.RequestPaused):
                    try:
                        await state.page.send(
                            uc.cdp.fetch.continue_request(request_id=event.request_id)
                        )
                    except Exception:
                        pass
                
                async def handle_auth_required(event: uc.cdp.fetch.AuthRequired):
                    _log("proxy_auth_requested", request_id=event.request_id)
                    challenge_response = uc.cdp.fetch.AuthChallengeResponse(
                        response="ProvideCredentials",
                        username=proxy_username,
                        password=proxy_password
                    )
                    try:
                        await state.page.send(
                            uc.cdp.fetch.continue_with_auth(
                                request_id=event.request_id,
                                auth_challenge_response=challenge_response
                            )
                        )
                        _log("proxy_auth_supplied", request_id=event.request_id)
                    except Exception as auth_err:
                        _log("proxy_auth_failed", error=str(auth_err))

                state.page.add_handler(uc.cdp.fetch.RequestPaused, handle_request_paused)
                state.page.add_handler(uc.cdp.fetch.AuthRequired, handle_auth_required)
                _log("proxy_auth_handler_registered")
            except Exception as e:
                _log("proxy_auth_setup_failed", error=str(e))
                
        _log("browser_started", headless=False, webgl_flags=True, webgl_spoofed=True, canvas_poisoning=True, chrome="google-chrome-stable", cdp_injected=True)

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
            description="Genera l'AOM Snapshot testuale della pagina (HTML distillato o Accessibility Tree nativo).",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["html", "ax"],
                        "description": "Seleziona la modalità: 'html' per l'HTMLParser distillato (default), 'ax' per l'Accessibility Tree nativo CDP."
                    }
                }
            }
        ),
        types.Tool(
            name="click",
            description="Clicca su un elemento specificato da riferimento (ref), selettore CSS, o coordinate (x, y).",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref": {"type": "string", "description": "Riferimento dell'elemento (es. 'e1') ottenuto da get_snapshot."},
                    "selector": {"type": "string", "description": "Selettore CSS dell'elemento."},
                    "x": {"type": "number", "description": "Coordinata X per il click."},
                    "y": {"type": "number", "description": "Coordinata Y per il click."}
                }
            }
        ),
        types.Tool(
            name="type",
            description="Inserisce del testo in un elemento specificato da riferimento (ref) o selettore CSS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref": {"type": "string", "description": "Riferimento dell'elemento (es. 'e1') ottenuto da get_snapshot."},
                    "selector": {"type": "string", "description": "Selettore CSS dell'elemento."},
                    "text": {"type": "string", "description": "Il testo da digitare."},
                    "clear": {"type": "boolean", "description": "Se True, cancella il contenuto esistente prima di digitare."}
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="evaluate",
            description="Esegue un'espressione JavaScript nella pagina attiva e restituisce il risultato.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "L'espressione JavaScript da valutare."}
                },
                "required": ["expression"]
            }
        ),
        types.Tool(
            name="wait",
            description="Attende la comparsa di un selettore o un ritardo in millisecondi.",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Selettore CSS da attendere."},
                    "timeout_ms": {"type": "integer", "description": "Tempo massimo di attesa in millisecondi per il selettore (default: 15000)."},
                    "delay_ms": {"type": "integer", "description": "Ritardo statico in millisecondi da attendere."}
                }
            }
        )
    ]

async def resolve_element(ref: str = None, selector: str = None):
    if not state.page:
        raise RuntimeError("Nessuna pagina attiva. Esegui prima il tool navigate.")
    
    if ref:
        if ref not in state.element_map:
            raise ValueError(f"Riferimento ref '{ref}' non trovato. Esegui get_snapshot per generare/aggiornare l'AOM.")
        
        if ref.startswith("ax"):
            el_info = state.element_map[ref]
            be_id = el_info.get("backend_node_id")
            if not be_id:
                raise ValueError(f"Nessun backend_node_id associato al riferimento AX '{ref}'.")
            
            # Resolve backend_node_id to RemoteObject
            remote_obj = await state.page.send(
                uc.cdp.dom.resolve_node(backend_node_id=be_id)
            )
            
            # Tag the element using call_function_on
            await state.page.send(
                uc.cdp.runtime.call_function_on(
                    function_declaration="function() { this.setAttribute('data-phantom-ref', '" + ref + "'); }",
                    object_id=remote_obj.object_id
                )
            )
            
            element = await state.page.select(f'[data-phantom-ref="{ref}"]')
            if not element:
                raise ValueError(f"Impossibile selezionare l'elemento taggato '{ref}'.")
            return element
            
        try:
            index = int(ref[1:])
        except Exception:
            raise ValueError(f"Formato ref '{ref}' non valido. Deve essere 'e<numero>'.")
        
        # Tag element on page in DOM order matching HTMLParser
        tagged = await state.page.evaluate(f"""(() => {{
            const elements = document.querySelectorAll('a, button, input');
            const el = elements[{index - 1}];
            if (el) {{
                el.setAttribute('data-phantom-ref', '{ref}');
                return true;
            }}
            return false;
        }})()""")
        
        if not tagged:
            raise ValueError(f"Elemento con riferimento '{ref}' (indice {index}) non trovato sulla pagina.")
        
        element = await state.page.select(f'[data-phantom-ref="{ref}"]')
        if not element:
            raise ValueError(f"Impossibile selezionare l'elemento taggato '{ref}'.")
        return element
        
    if selector:
        element = await state.page.select(selector)
        if not element:
            raise ValueError(f"Elemento con selettore CSS '{selector}' non trovato.")
        return element
        
    raise ValueError("Fornire 'ref' o 'selector' per identificare l'elemento.")

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    global _active_sessions
    
    # Auto-recover target swaps (e.g. cross-origin isolation)
    if state.browser and getattr(state, "page", None):
        try:
            await state.page.send(uc.cdp.runtime.evaluate(expression="1"))
        except Exception:
            try:
                await state.browser.update_targets()
                if state.browser.tabs:
                    state.page = state.browser.main_tab
                    # Reinject the stealth script onto the new target
                    await state.page.send(uc.cdp.page.enable())
                    await state.page.send(uc.cdp.page.add_script_to_evaluate_on_new_document(source=STEALTH_INJECTION_PAYLOAD))
                    _log("target_swap_recovered", tab_id=getattr(state.page, "target_id", "unknown"))
            except Exception as recover_err:
                _log("target_swap_recovery_failed", error=str(recover_err))
                
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
            try:
                await state.page.get(arguments["url"])
            except Exception as e:
                _log("navigate_auto_recover", error=str(e))
                if state.browser:
                    try:
                        state.browser.stop()
                    except Exception:
                        pass
                state.browser = None
                state.page = None
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
            
            mode = arguments.get("mode", "html")
            if mode == "ax":
                await state.page.send(uc.cdp.accessibility.enable())
                nodes = await state.page.send(uc.cdp.accessibility.get_full_ax_tree())
                
                # Clear previous element_map to avoid stale mappings
                state.element_map = {}
                
                ax_buffer = []
                ax_counter = 1
                for node in nodes:
                    if node.ignored:
                        continue
                    
                    role_str = node.role.value if (node.role and node.role.value) else "UNKNOWN"
                    name_str = node.name.value if (node.name and node.name.value) else ""
                    val_str = node.value.value if (node.value and node.value.value is not None) else None
                    
                    ref_id = f"ax{ax_counter}"
                    ax_counter += 1
                    
                    # Store mapping in element_map
                    state.element_map[ref_id] = {
                        "tag": role_str.upper(),
                        "context": name_str or (val_str if val_str is not None else ""),
                        "backend_node_id": node.backend_dom_node_id,
                        "selector": None
                    }
                    
                    desc = f"[{ref_id}: {role_str.upper()}"
                    if name_str:
                        desc += f" '{name_str}'"
                    if val_str is not None:
                        desc += f" value='{val_str}'"
                    desc += "]"
                    ax_buffer.append(desc)
                    
                dist = " ".join(ax_buffer)
                duration_ms = int((time.monotonic() - start) * 1000)
                _log("tool_ok", tool="get_snapshot", mode="ax", duration_ms=duration_ms, snapshot_len=len(dist))
                return [types.TextContent(type="text", text=f"--- AX SNAPSHOT ---\n\n{dist}\n\n--- END SNAPSHOT ---")]
            
            else: # html mode
                html = await state.page.get_content()
                parser = AOMDistiller()
                parser.feed(html)
                state.element_map = parser.elements
                dist = ' '.join(parser.text_buffer)
                duration_ms = int((time.monotonic() - start) * 1000)
                _log("tool_ok", tool="get_snapshot", mode="html", duration_ms=duration_ms, snapshot_len=len(dist))
                return [types.TextContent(type="text", text=f"--- AOM SNAPSHOT ---\n\n{dist}\n\n--- END SNAPSHOT ---")]
            
        elif name == "click":
            if not state.page:
                raise RuntimeError("Nessuna pagina attiva. Esegui prima il tool navigate.")
                
            ref = arguments.get("ref")
            selector = arguments.get("selector")
            x = arguments.get("x")
            y = arguments.get("y")
            
            if ref or selector:
                element = await resolve_element(ref=ref, selector=selector)
                await element.mouse_click()
                target_desc = f"ref '{ref}'" if ref else f"selector '{selector}'"
            elif x is not None and y is not None:
                await state.page.mouse_click(int(x), int(y))
                target_desc = f"coordinate ({x}, {y})"
            else:
                raise ValueError("Specificare 'ref', 'selector' o le coordinate 'x' e 'y' per eseguire il click.")
                
            duration_ms = int((time.monotonic() - start) * 1000)
            _log("tool_ok", tool="click", target=target_desc, duration_ms=duration_ms)
            return [types.TextContent(type="text", text=f"Click eseguito con successo su {target_desc}.")]
            
        elif name == "type":
            ref = arguments.get("ref")
            selector = arguments.get("selector")
            text = arguments.get("text")
            clear = arguments.get("clear", False)
            
            if not text and text != "":
                raise ValueError("Il parametro 'text' è obbligatorio.")
                
            element = await resolve_element(ref=ref, selector=selector)
            if clear:
                unique_selector = f'[data-phantom-ref="{ref}"]' if ref else selector
                await state.page.evaluate(f'''(() => {{
                    const el = document.querySelector({json.dumps(unique_selector)});
                    if (el) {{
                        el.value = "";
                        el.dispatchEvent(new Event("input", {{ bubbles: true }}));
                        el.dispatchEvent(new Event("change", {{ bubbles: true }}));
                    }}
                }})()''')
                
            await element.send_keys(text)
            target_desc = f"ref '{ref}'" if ref else f"selector '{selector}'"
            
            duration_ms = int((time.monotonic() - start) * 1000)
            _log("tool_ok", tool="type", target=target_desc, duration_ms=duration_ms)
            return [types.TextContent(type="text", text=f"Digitazione completata con successo su {target_desc}.")]
            
        elif name == "evaluate":
            expression = arguments.get("expression")
            if not expression:
                raise ValueError("Il parametro 'expression' è obbligatorio.")
                
            if not state.page:
                raise RuntimeError("Nessuna pagina attiva. Esegui prima il tool navigate.")
                
            res = await state.page.evaluate(expression)
            duration_ms = int((time.monotonic() - start) * 1000)
            _log("tool_ok", tool="evaluate", expression=expression, duration_ms=duration_ms)
            return [types.TextContent(type="text", text=json.dumps(res, ensure_ascii=False))]
            
        elif name == "wait":
            selector = arguments.get("selector")
            timeout_ms = arguments.get("timeout_ms", 15000)
            delay_ms = arguments.get("delay_ms")
            
            if not state.page:
                raise RuntimeError("Nessuna pagina attiva. Esegui prima il tool navigate.")
                
            desc_list = []
            if delay_ms is not None:
                await asyncio.sleep(float(delay_ms) / 1000.0)
                desc_list.append(f"ritardo statico di {delay_ms}ms")
                
            if selector:
                timeout_s = float(timeout_ms) / 1000.0
                element = await state.page.select(selector, timeout=timeout_s)
                if not element:
                    raise asyncio.TimeoutError(f"Selettore '{selector}' non apparso entro {timeout_s} secondi.")
                desc_list.append(f"selettore '{selector}'")
                
            if not desc_list:
                raise ValueError("Specificare almeno 'selector' o 'delay_ms' per l'attesa.")
                
            desc = " e ".join(desc_list)
            duration_ms = int((time.monotonic() - start) * 1000)
            _log("tool_ok", tool="wait", desc=desc, duration_ms=duration_ms)
            return [types.TextContent(type="text", text=f"Attesa completata con successo per: {desc}.")]
            
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
    except asyncio.CancelledError:
        raise
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
        # Share SseServerTransport per token to support concurrent browser sessions/tabs.
        if token not in sse_transports:
            transport = SseServerTransport(f"/messages/t/{quote(token, safe='')}")
            sse_transports[token] = transport
        else:
            transport = sse_transports[token]
        
        try:
            async with transport.connect_sse(scope, receive, send) as streams:
                try:
                    await _run_mcp_with_discover_guard(streams[0], streams[1])
                except Exception as mcp_err:
                    _log("mcp_run_error", error=str(mcp_err))
        except anyio.ClosedResourceError:
            _log("sse_stream_closed_by_client")
        except Exception as e:
            _log("sse_stream_error", error=str(e), error_type=type(e).__name__)
        finally:
            # Do not pop transport from sse_transports on disconnect, as other tabs/sessions
            # may still be using the shared transport instance.
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

async def debug_chrome(request: Request):
    """Diagnostic route to execute google-chrome-stable directly and capture its launch output."""
    import subprocess
    cmd = [
        "/usr/bin/google-chrome-stable",
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--use-gl=angle",
        "--use-angle=swiftshader-webgl",
        "--enable-unsafe-swiftshader",
        "--ignore-gpu-blocklist",
        "--enable-webgl",
        "--remote-debugging-port=9222"
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.sleep(2.0)
        returncode = proc.returncode
        stdout, stderr = b"", b""
        if returncode is not None:
            stdout, stderr = await proc.communicate()
        else:
            proc.terminate()
            stdout, stderr = await proc.communicate()
            
        return JSONResponse({
            "returncode": returncode,
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
            "env_display": os.getenv("DISPLAY", "None")
        })
    except Exception as e:
        return JSONResponse({"error": str(e)})

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
        Route("/debug_chrome", endpoint=debug_chrome),
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
