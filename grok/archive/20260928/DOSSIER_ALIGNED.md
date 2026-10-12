# Operator map

Architecture and Grok CLI settings for this workdir. CWD: `/Users/daniele_palagi/Desktop/phantom_cloud`.

## Identity

Stealth-browser MCP (nodriver + Starlette/SSE) with an AOM distillation layer. Engine file: `phantom_cloud.py`.

| Source | Fact |
|--------|------|
| `fly.toml` | App `phantom-cloud-engine`, `primary_region = 'fra'`, `[build] dockerfile = 'Dockerfile'` |
| `fly.toml` | HTTP service internal port `8000`, `force_https = true`, auto-stop and auto-start |
| `fly.toml` | `min_machines_running = 1`; connection concurrency soft `20` / hard `25` |
| `fly.toml` | One shared CPU, `1gb` memory |
| README | Public hostname `https://phantom-cloud-engine.fly.dev` |
| README | Deploy is scaled to exactly one machine so SSE session state stays on that process |

`fly.toml` records the scale as `min_machines_running = 1`. The README is the source that ties that single machine to stateful SSE session affinity.

## Runtime

Image (`Dockerfile`): `python:3.11-slim`, Google Chrome stable (`.deb`), Xvfb, xauth, procps. Process command:

`xvfb-run -a --server-args='-screen 0 1920x1080x24' python phantom_cloud.py`

Listens on `8000`. Python deps in `requirements.txt`: `nodriver>=0.30`, `mcp==1.0.0`, `starlette`, `uvicorn`, `sse-starlette`, `httpx>=0.25.0`.

README local packages: `google-chrome-stable`, `xvfb` / `xvfb-run`, `procps` (`pkill`). README local venv path: `/tmp/phantom_venv` (not required on the Fly image). README also documents `.venv/bin/python -m pytest tests/` for in-process tests.

Env names from `.env.example` only: `PORT`, `UNKEY_ROOT_KEY`, `UNKEY_API_ID`, and a commented client `TOKEN`. `.env` is gitignored. Do not open it.

## Request path

1. Client opens `GET /sse/?token=<token>`. The trailing slash after `/sse/` is required. Full form: `https://phantom-cloud-engine.fly.dev/sse/?token=<token>`.
2. The session advertises `POST /messages/t/<token>` (token in the path, not the query).

Auth: Unkey v2 when `UNKEY_ROOT_KEY` is set. When that variable is unset, the service accepts a token whose prefix is `ph_live_` (`.env.example` and README).

## Production tool surface

Six tools. There is no seventh.

| Tool | Inputs |
|------|--------|
| `navigate` | `url` |
| `get_snapshot` | `mode`: `html` (default) or `ax` |
| `click` | `ref`, else `selector`, else `x`,`y` |
| `type` | `ref` or `selector`, `text`, optional `clear` |
| `evaluate` | `expression` |
| `wait` | `selector`, `timeout_ms`, `delay_ms` (selector, delay, or both in sequence) |

`html` refs are `e*` (`e1`, `e2`, …). `ax` refs are `ax*` (`ax1`, `ax2`, …). The last `get_snapshot` mode owns the refs.

## Repo layout

| Path | Role |
|------|------|
| `AGENTS.md` | Project instructions (inspect may show `Agents.md`) |
| `phantom_cloud.py` | Engine |
| `Dockerfile`, `fly.toml`, `requirements.txt` | Image, Fly app, Python deps |
| `.env.example` | Env-name template |
| `tests/` | pytest and harness scripts |
| `reports/` | Local records (gitignored). Pointer: `reports/SMOKE.md` |
| `runs/` | Telemetry archives (gitignored). Not the CLI contract |
| `commercial/` | `ONBOARDING_CHECKLIST.md`, `PILOT_OFFER.md`, `PRICING_FRAME.md`, `ROE_AND_SCOPE.md` |
| `.grok/` | This map and the project CLI files already in the tree |
| `smoke_test.py` | Root smoke client |

Protected unless the task names the file: `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`.

## Grok CLI in this workdir

Default start:

```bash
cd /Users/daniele_palagi/Desktop/phantom_cloud
grok --effort xhigh --no-subagents --disable-web-search
```

A project agent file is present. To use it, add:

```bash
--agent-profile .grok/agents/phantom-surgery.md
```

Project `.grok/config.toml` applies `[mcp_servers]`, `[plugins]`, `[permission]`, and `[mcp]`.

Folder trust (`grok --trust` or `/hooks-trust`) is required before `AGENTS.md` and project skills load. This folder is trusted in `~/.grok/trusted_folders.toml`. `AGENTS.md` is present at the checkout root; inspect project instructions are > 0.

MCP URL in project config (token is the env placeholder only):

```
https://phantom-cloud-engine.fly.dev/sse/?token=${PHANTOM_AUTH_TOKEN}
```

Server name: `phantom-cloud-engine`, type `sse`. Set `PHANTOM_AUTH_TOKEN` in the environment. Do not paste a live key into the file.

`grok inspect` (1.0.41 stable, this CWD; no secrets in the output):

- Project trusted: **yes**
- Project instructions: **1** (`AGENTS.md` / `Agents.md`, ~244 tokens)
- MCP: `phantom-cloud-engine` (sse), from project config
- Project agent: `phantom-surgery`
- Project skill: `phantom-matrix` (present; model invocation disabled)
- Hooks: none from this project (Vercel plugin is user-global)
- `[privacy]` warning is from `~/.grok/config.toml`, not this project file

## Evidence index

- `reports/SMOKE.md` names archive `runs/prod_postdeploy_20260924T153949Z`.
- `runs/` is gitignored telemetry. It is not the CLI contract.
- This map does not score archives.

## Out of scope

Do not copy a chat-sandbox tree into this checkout. Do not dump secrets or open `.env`. Do not `fly deploy` unless asked. Do not edit the four protected engine files unless the task names them.
