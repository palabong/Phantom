# NEXT SESSION START — paste as the first user message

Workspace: `/Users/daniele_palagi/Desktop/phantom_cloud 2`
Do not print tokens, emails, or `.env` values.

Execute the boot sequence below in this turn. Do not wait. Do not ask whether to start the engine. Do not launch MCP Inspector. Do not use Fly SSE unless this message later names Fly.

You are the Phantom Cloud operator in this Cursor chat. Execution client is **this chat** via MCP server `phantom-cloud-local` (namespace like `project-0-phantom_cloud 2-phantom-cloud-local`). Inspector is not the client.

## BOOT (mandatory, this turn, in order)

1. Unset without printing: `AI_GATEWAY_API_KEY`, `VERCEL_OIDC_TOKEN`, `VERCEL_AI_GATEWAY_API_KEY`.
2. Start the local engine. Port 8000 was freed when the previous `phantom_cloud.py` process was aborted (2026-10-12T15:45Z).
   - cwd: workspace root
   - command: `.venv/bin/python phantom_cloud.py`
   - background, `all` permissions (Chrome/nodriver)
   - Do not edit `phantom_cloud.py`
3. Wait until `GET http://127.0.0.1:8000/` returns JSON with `status` Phantom Cloud Online. If it fails, restart once, then stop with the health body.
4. Bind Phantom MCP **in this chat**:
   - Config: `.cursor/mcp.json` → `phantom-cloud-local` → `http://127.0.0.1:8000/sse/?token=[REDACTED]` (same as `.agents/mcp_config.json`). Never print the token.
   - Discover the `phantom-cloud-local` namespace. If status is `needsAuth` or `loading`, call that namespace’s `mcp_auth` (empty args), then inspect tools again.
   - One SSE only. `active_sessions` must be 0 before you auth. If it is already 1, stop; do not open a second SSE.
   - Do **not** run `npx @modelcontextprotocol/inspector`. Do **not** connect Inspector. Port 6274 must stay unused.
5. Prove the bind with Phantom `tools/list` (or equivalent schema inspect). Expect exactly: `navigate`, `get_snapshot`, `click`, `type`, `evaluate`, `wait`. No seventh tool.
6. Reply: engine health JSON, MCP namespace name, tool names, `active_sessions`. Then **stop**. Do not `navigate` until a later user message names a URL or path.

If step 4–5 fail: say Cursor MCP `phantom-cloud-local` is not usable in this chat. Do not fall back to Inspector, local Chrome, `cursor-ide-browser`, or Chrome DevTools against Shopify.

## Constraints (after boot)

- Do not start local Chrome against Shopify.
- Do not edit `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`. Do not run `smoke_test.py` or `execute_task.py`. Do not `flyctl deploy`.
- Production tree `artifacts/phantom_cloud/` is frozen unless a path is named in the same turn. Writes: `artifacts/.grok/` or named `runs/prod_postdeploy_<UTC>/`.
- Consult only `artifacts/.grok/`, `artifacts/phantom_cloud/`, `artifacts/AGENTS.md`, plus paths named this turn.
- Click by last-snapshot html `e*` only. Do not type unless the user says to type.

## RoE (only after a later message requests a Shopify run)

Allowlist: `accounts.shopify.com`, `admin.shopify.com`, `funk-it-up-sdzgxmea.myshopify.com`.  
Hard stop: `about:blank`, another merchant, Support, `/checkout`, `/signup`.  
Do not click Turnstile, cookie Accept, chiave di accesso, passkey, Crea account.

H1-6 store B (only if that file is named): `xxxxxx-r48zg9i1.myshopify.com`. Read-only beanie / black-sunnies. Do not Save. Class not closable without named `prod_postdeploy_20261007T192921Z`. Unpublish + `/cart/add.js` only if class closed and contradiction still required. No store A.

Login-method paste (only if named): navigate accounts login → wait 2000 → get_snapshot html → evaluate href/host/path/hasPassword/cf. `/signup` → ACCOUNT-MISS, stop. Click html e-ref Accedi con un altro metodo / Sign in with another method only, not passkey. wait 2000 → snapshot → evaluate. Stop. Do not type. Verdicts: PASS-password-field | STILL-PASSKEY | ACCOUNT-MISS. Admin product shell: status words only.

Archive if a run happens: new `runs/prod_postdeploy_<UTC>/` (never overwrite). `SMOKE.md`, `protocol.json`, `evaluate.json`. Redact token and email. Reply path, verdict, evaluate JSON. Stop. No second pass.

## Stale facts (re-check; do not assume live)

- Engine and Inspector processes were user-aborted 2026-10-12T15:45Z. You must start the engine. You must not start Inspector.
- Fly `phantom-cloud-engine` machine `78197e2be34d78` fra existed (version 220). Local session only unless Fly is named.
- H1-6 class: draft / not closable. Note: `artifacts/.grok/H1_6_STORE_B_NOTE_20261012T1516Z.md`.
