PROJECT: phantom_cloud
UPDATED: 2026-09-30T23:45Z
ENVIRONMENT: Official Grok Build 4.7 High — MCP Inspector + local Phantom
ASSUME: phantom_cloud.py already on :8000 AND MCP Inspector already connected. Do not restart them. Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.

CWD: /Users/daniele_palagi/Desktop/phantom_cloud
Inspector already on http://127.0.0.1:8000/sse/?token=<REDACTED>
Token → [REDACTED]. Never print. Never write to runs/.
One SSE session. Tools: navigate, get_snapshot, click, type, evaluate, wait.
Click only last-snapshot ref. No passwords this turn. No Turnstile solver. No Support.
Do not drive Chrome outside Inspector. Do not start a second session.

ALLOWLIST
- accounts.shopify.com
- partners.shopify.com
- admin.shopify.com
- www.shopify.com only if path matches ^/([a-z]{2}/)?partners
HARD STOP: about:blank, other merchants, Support, /checkout, www.shopify.com outside /partners*.
partners.shopify.com → www.shopify.com/nl/partners (or /de /it /en) is ALLOWED. Continue.

P0 — full run
1. tools/list (must be the six tools; if not, reconnect Inspector to the same :8000 SSE, then list again. Do not stop the run.)
2. navigate {"url":"https://accounts.shopify.com/"}
3. wait {"delay_ms":8000}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:!!(document.querySelector('[name=cf-turnstile-response],#challenge-form,.cf-turnstile')||/just a moment|ci siamo quasi|un moment/i.test(document.title))})"}
5. get_snapshot {"mode":"html"}
6. If cf: wait {"delay_ms":8000}, evaluate the same expression again. No type. No checkbox click.
7. navigate {"url":"https://partners.shopify.com/"}
8. wait {"delay_ms":3000}
9. evaluate the same expression. If host is www.shopify.com and path matches /partners*: continue.
10. get_snapshot {"mode":"ax"}
11. If snapshot has Accedi / Log in / Iscriviti / Sign in (not Accetta tutti / cookie): click that ref, wait {"delay_ms":2000}, evaluate again.
12. If after that click host is accounts.shopify.com or admin.shopify.com: evaluate hasEmail/hasPassword/cf once more.
13. Do not click Accetta tutti. Do not fill email. Do not open Support.

Verdict
- PASS-engine: hasEmail or hasPassword true AND cf false.
- NAV-ok: partners /partners* loaded AND accounts still cf. Not a bounty.
- FAIL-engine: tools/list missing or tab left allowlist.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
source: inspector+local-phantom
inspectorConnected: true
server_url: http://127.0.0.1:8000/sse  (no token)

Reply: Inspector up, path, matrix, evaluate JSON, final href. Stop.
