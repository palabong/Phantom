PROJECT: phantom_cloud
UPDATED: 2026-09-29T17:14Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Antigravity CLI (Agent Mode)

CWD: device production tree (Drive phantom_cloud).
Inspector already on https://phantom-cloud-engine.fly.dev
Do not restart. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. Never print it. Never write it to disk. One session.

Fixes vs 20260929T112017Z (do not repeat):
- SMOKE.md must include Target, Server, Sessions, Verdict, Reason, Final href, step table.
- protocol.json must be an object with timestamp, target_url, server_url, sessions, verdict, reason, final_href, results[].
- evaluate.json must be an object (already ok). Never a raw string.
- Archive dir MUST be runs/prod_postdeploy_<YYYYMMDDTHHMMSSZ>/ — never runs/prod_postdeploy_/
- hasPasswordForm uses ONLY input[type=password],input[name=password] — never a generic form.
- click uses {"ref":"<eN or axN from the snapshot taken immediately before>"} — never selector "a, button".
- click miss uses {"ref":"#phantom-missing-target"} — never CSS selector mode if the tool takes ref.
- Do not click cookie Accept/Decline, Log in, Checkout, owner login.
- Gate on /password is optional. Catalog on / is also PASS. Do not fail if hasPasswordForm is false.
- No example.com. No stealth essay. No smoke_test_output.txt.

Allowlist host: funk-it-up-sdzgxmea.myshopify.com
Allowlist paths this run: / and /password only.
Hard stop if about:blank OR hostname ≠ funk-it-up-sdzgxmea.myshopify.com.
Do not open admin, partners, accounts, other shops, Support.
Do not type the storefront password. Do not persist PII.

Sequence:
1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/"}
3. wait {"delay_ms":500}
4. get_snapshot {"mode":"html"}
5. get_snapshot {"mode":"ax"}
6. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]')})"}
7. type N/A. Do not invent a password.
8. click hit: parse the LAST snapshot (ax, step 5). Pick one visible BUTTON or A that is NOT Accept, Decline, Manage preferences, Log in, Checkout, Close. Use that ref only, e.g. {"ref":"ax15"}. If none safe: status N/A, do not click.
9. click miss: {"ref":"#phantom-missing-target"} — not-found is PASS.

Pass: six tools listed, final host allowlisted, path / or /password, archive complete with verdict field.
Not a bounty finding.

Archive:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,ax_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token.

SMOKE.md template:
# Production smoke <UTC>
Target: `https://funk-it-up-sdzgxmea.myshopify.com/`
Server: `https://phantom-cloud-engine.fly.dev`
Sessions: 1
Verdict: `PASS` or `FAIL` or `HARD_STOP`
Reason: `<short>`
Final href: `<href>`

| step | status | latency_ms | details |
|---|---|---|---|
| … | … | … | … |

protocol.json results[]: {tool, status, latency_ms, details} per step. No raw token.

Reply only: path, matrix, evaluate JSON, final href. Stop.
