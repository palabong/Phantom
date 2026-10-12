PROJECT: phantom_cloud
UPDATED: 2026-09-30T23:22Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running in this CLI terminal

CWD: device production tree (Drive phantom_cloud).
Inspector is UP. Do not start a second Inspector. Do not start a second SSE.
Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Do not drive Chrome outside Inspector. Do not AppleScript. Do not local-chrome operator flow.

Token → already in the Inspector SSE URL / PHANTOM_AUTH_TOKEN. Never print it. Never write it to runs/.
Six tools only: navigate, get_snapshot, click, type, evaluate, wait.
Click payload: {"ref":"<eN or axN from the snapshot immediately before>"}.
type this run: N/A (no secret supplied).

H1-0 purpose: prove the Phantom pipe on researcher storefront A with stealth navigate + AOM. Not a bounty. Not login.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
ALLOWLIST paths: / and /password only
HARD STOP: about:blank OR hostname ≠ funk-it-up-sdzgxmea.myshopify.com OR Support OR admin.shopify.com OR accounts.shopify.com OR another shop.
Do not type the storefront password. Do not checkout. Do not click cookie Accept/Decline.

Record which SSE the existing Inspector is attached to (no token query):
- http://127.0.0.1:8000/sse/  OR
- https://phantom-cloud-engine.fly.dev/sse/
If tools/list does not return the six tools: FAIL-engine, archive, stop. Do not "fix" by opening desktop Chrome.

Sequence
1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/"}
3. wait {"delay_ms":1500}
4. get_snapshot {"mode":"html"}
5. get_snapshot {"mode":"ax"}
6. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),cf:!!(document.querySelector('[name=cf-turnstile-response],#challenge-form,.cf-turnstile')||/just a moment|ci siamo quasi/i.test(document.title)),webdriver:navigator.webdriver===true,hasChrome:typeof window.chrome==='object',ua:navigator.userAgent.slice(0,80)})"}
7. type N/A
8. click hit: from the LAST ax snapshot pick one visible BUTTON or A that is NOT Accept, Decline, Manage preferences, Log in, Checkout, Close. Payload {"ref":"axN"}. If none safe: status N/A, do not click.
9. wait {"delay_ms":500}
10. click miss: {"ref":"#phantom-missing-target"} — not-found is PASS
11. evaluate the same expression as step 6 (final href/host/path)

PASS-engine when:
- six tools listed
- final host is funk-it-up-sdzgxmea.myshopify.com
- path is / or /password
- evaluate is an object
- click-miss returned a controlled not-found
- archive complete

FAIL-engine when Inspector has no six tools, or navigate never leaves about:blank, or host leaves allowlist.
cf true on this storefront is recorded, not a ticket.
webdriver true is a stealth caveat (L4), not a Shopify finding. Do not write “SwiftShader solved”.

Archive on the device tree:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,ax_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token.

SMOKE.md must include: Target, Server (no token), Sessions, Verdict, Reason, Final href, step table.
protocol.json object: timestamp, target_url, server_url, source:"inspector+phantom", inspectorConnected:true, sessions, verdict, reason, final_href, results[].
evaluate.json object (not a string).

Reply only: Inspector attached yes/no, server_url without token, path, matrix, evaluate JSON, final href. Stop.
