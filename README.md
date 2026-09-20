# phantom_cloud

Stealth browser MCP server (nodriver + Starlette/SSE).

Implements the Phantom Architecture / AOM Distillation layer for WAF-resistant navigation and low-token Accessibility Object Model snapshots intended for AI-agent and security-team consumption.

## Production surface

| Item | Value |
|------|-------|
| Tools | `navigate`, `get_snapshot` |
| Auth | Unkey v2 when `UNKEY_ROOT_KEY` is set; otherwise token prefix `ph_live_` fallback |
| Deploy target | Fly.io app `phantom-cloud-engine` (region `fra`) |
| Runtime | Python 3.11+, Google Chrome stable, Xvfb |

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

Run (development):

```bash
source /tmp/phantom_venv/bin/activate
xvfb-run -a --server-args='-screen 0 1920x1080x24' python phantom_cloud.py
```

## Deployment

```bash
fly secrets set UNKEY_ROOT_KEY=unkey_xxxxxxxx -a phantom-cloud-engine
fly deploy -a phantom-cloud-engine
```

Connect:

```
https://phantom-cloud-engine.fly.dev/sse/?token=<your_end_user_key>
```

Cold-start machines may reject the first `navigate`; subsequent calls succeed.

## Constraints

- Do not modify `phantom_cloud.py`, `Dockerfile`, `fly.toml`, or `requirements.txt` without explicit task instruction.
- Prefer additive, reversible changes.
- Production readiness and monetisation path take priority.
