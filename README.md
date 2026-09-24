# phantom_cloud

Stealth browser MCP server (nodriver + Starlette/SSE).

Implements the Phantom Architecture / AOM Distillation layer for WAF-resistant navigation and low-token Accessibility Object Model snapshots intended for AI-agent and security-team consumption.

## Production surface

| Item | Value |
|------|-------|
| Tools | `navigate`, `get_snapshot`, `click`, `type`, `evaluate`, `wait` |
| Auth | Unkey v2 when `UNKEY_ROOT_KEY` is set; otherwise token prefix `ph_live_` fallback |
| Deploy target | Fly.io app `phantom-cloud-engine` (region `fra`) — **Scaled to exactly 1 machine** to guarantee stateful memory-based SSE session affinity |
| Runtime | Python 3.11+, Google Chrome stable, Xvfb |

### Tool Descriptions & Schemas

#### Core Tools
* **`navigate`**: Navigates to a target URL bypassing WAF checks.
  * Inputs: `{"url": "<url>"}`
* **`get_snapshot`**: Generates a textual AOM (Accessibility Object Model) representation of the active page. **HTML AOM remains the default mode for full backward compatibility.**
  * Inputs: `{ "mode": "html" | "ax" }`
  * Modes:
    * `"html"` (default): Uses the custom `AOMDistiller` (HTMLParser) to build a semantic node layout (mapped via stable `e1`, `e2`... refs).
    * `"ax"`: Fetches the native Chrome Accessibility Tree via CDP (Accessibility domain), stripping out ignored elements and mapping stable `ax1`, `ax2`... refs to backend node IDs.

#### New Interaction Tools
* **`click`**: Simulates a realistic hardware-like mouse click on an element or specific coordinates.
  * Inputs: `{ "ref": "e1"|"ax1", "selector": "#btn", "x": 100, "y": 100 }` (Priority: `ref` > `selector` > coordinates `x,y`).
* **`type`**: Types text character-by-character into an input element.
  * Inputs: `{ "ref": "e1"|"ax1", "selector": "#input", "text": "value", "clear": true|false }`
* **`evaluate`**: Evaluates a raw JavaScript expression on the page and returns the serialized result.
  * Inputs: `{ "expression": "document.title" }`
* **`wait`**: Performs an explicit wait for a CSS selector or a static delay (or both sequentially).
  * Inputs: `{ "selector": ".card", "timeout_ms": 15000, "delay_ms": 1000 }`

## Authentication (current)

- Server requires environment variable `UNKEY_ROOT_KEY` (Unkey root key, starts with `unkey_`).
- Clients send the end-user key as query parameter: `?token=<key_secret>`
- Endpoint form: `/sse/?token=<key_secret>`
- Messages endpoint is advertised as `/messages/t/<key_secret>` (path segment, not query) so MCP Inspector does not encode `?` into the path.
- `server/discover` (MCP 2026-07-28 probe) is answered with JSON-RPC `-32601` so the SSE session is not torn down; clients may then send legacy `initialize`.

## Local development environment

The artifacts filesystem does not support venv symlinks. Use a temporary venv:

```bash
python3 -m venv /tmp/phantom_venv
source /tmp/phantom_venv/bin/activate
pip install -r requirements.txt
```

Required system packages:

- `google-chrome-stable`
- `xvfb` / `xvfb-run`
- `procps` (specifically `pkill` to support browser pre-start and failure cleanup processes)

Run (development):

```bash
source /tmp/phantom_venv/bin/activate
xvfb-run -a --server-args='-screen 0 1920x1080x24' python phantom_cloud.py
```

### Running Tests

We have comprehensive in-process mock and integration test suites written in `pytest`. To execute them:

```bash
# Run all tests (including AX snapshots & interaction tool tests)
.venv/bin/python -m pytest tests/
```

Individual test files:
* **`tests/test_interaction_tools.py`**: Verifies tool registration, `evaluate` calculations, `wait` delays, and controlled uninitialized page failures.
* **`tests/test_ax_snapshot.py`**: Verifies `get_snapshot` HTML mode vs native AX mode behaviors under mocked page and synthetic tree states.

## Deployment

```bash
fly secrets set UNKEY_ROOT_KEY=unkey_xxxxxxxx -a phantom-cloud-engine
fly deploy -a phantom-cloud-engine
```

Connect:

```
https://phantom-cloud-engine.fly.dev/sse/?token=<your_end_user_key>
```

**Note on Cold-Start Remediation:**
The server is configured with `min_machines_running = 1` in `fly.toml` and scaled to exactly `1` machine. This keeps a single instance warm continuously, eliminating cold starts during active pipelines. Additionally, a dynamic runtime monkey-patch (`patch_nodriver()`) extends `nodriver`'s browser connection timeout from 2.5 seconds to **15 seconds (30 attempts)**, and proactive process cleanups sanitize zombie browser instances to guarantee absolute connection reliability.

## Constraints

- Do not modify `phantom_cloud.py`, `Dockerfile`, `fly.toml`, or `requirements.txt` without explicit task instruction.
- Prefer additive, reversible changes.
- Production readiness and monetisation path take priority.
