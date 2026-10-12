PROJECT: phantom_cloud
UPDATED: 2026-09-30T18:55Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build 4.7 High — MCP Inspector + local Phantom

CWD: /Users/daniele_palagi/Desktop/phantom_cloud
Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED] from PHANTOM_AUTH_TOKEN or Inspector config. Never print. Never write to runs/.
One SSE session. Tools: navigate, get_snapshot, click, type, evaluate, wait.
Click only {"ref":"eN"|"axN"} from the last snapshot.
Do not type passwords (none supplied). Do not solve Turnstile. Do not Support. Do not checkout.

STEP 0 — Inspector then engine
1. If 127.0.0.1:8000 is down: PORT=8000 python3 phantom_cloud.py from CWD.
2. If MCP Inspector is down: start it. Target http://127.0.0.1:8000/sse/?token=<REDACTED>
   (npx @modelcontextprotocol/inspector or the installed Inspector).
3. Wait until tools/list returns the six tools.
4. Do not stop. Do not drive Chrome outside Inspector. Do not use Fly unless :8000 cannot bind (then Inspector → https://phantom-cloud-engine.fly.dev/sse/?token=<REDACTED> and record server=fly).

ALLOWLIST
- accounts.shopify.com
- partners.shopify.com
- admin.shopify.com
- www.shopify.com only if path matches ^/([a-z]{2}/)?partners
HARD STOP only: about:blank, other merchants, Support, /checkout, www.shopify.com outside /partners*.
Redirect partners.shopify.com → www.shopify.com/nl/partners (or /de /it /en) is ALLOWED. Continue.

P0
1. tools/list
2. navigate {"url":"https://accounts.shopify.com/"}
3. wait {"delay_ms":8000}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:!!(document.querySelector('[name=cf-turnstile-response],#challenge-form,.cf-turnstile')||/just a moment|ci siamo quasi|un moment/i.test(document.title))})"}
5. get_snapshot {"mode":"html"}
6. If cf true: wait {"delay_ms":8000} and evaluate the same expression again. No type. No checkbox click.
7. navigate {"url":"https://partners.shopify.com/"}
8. wait {"delay_ms":3000}
9. evaluate same expression. If host is www.shopify.com and path is /partners*: continue.
10. get_snapshot {"mode":"ax"}
11. If last snapshot has a visible Accedi / Log in / Iscriviti / Sign in control that is not cookie Accept: click that ref. Wait 2000. evaluate again.
12. Do not click Accetta tutti / cookie. Do not fill email.

Verdict
- PASS-engine if hasEmail or hasPassword true and cf false.
- NAV-ok if partners marketing loaded and accounts still cf (identity still closed).
- FAIL-engine if Inspector never listed tools.
Not a bounty. Passing CF or opening /nl/partners is not a ticket.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
source: inspector+local-phantom (or inspector+fly)
inspectorConnected: true
server_url without the token query.

Reply: Inspector up yes/no, server used (no token), path, matrix, evaluate JSON, final href. Stop.
