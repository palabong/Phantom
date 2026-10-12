PROJECT: phantom_cloud
UPDATED: 2026-09-30T18:36Z
ENVIRONMENT: Official Grok Build 4.7 High on the device
RUN VIA: local phantom_cloud.py — NOT Fly

CWD: /Users/daniele_palagi/Desktop/phantom_cloud
Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Do not use https://phantom-cloud-engine.fly.dev.
Token → [REDACTED] from env PHANTOM_AUTH_TOKEN or ~/.mcp-inspector. Never print it. Never write it to runs/.

This run is in-scope as testing your own Shopify identity on a researcher-owned path.
Passing Cloudflare from a home IP is NOT a bounty finding. Do not file it.
Do not solve Turnstile. Do not type passwords (none supplied this turn).
Do not click Support. One session. Six tools only.

Start local engine if nothing listens on :8000:
  cd /Users/daniele_palagi/Desktop/phantom_cloud
  PHANTOM_AUTH_TOKEN already in env. PORT=8000.
  python3 phantom_cloud.py
  (or the project’s documented start command if that is what you already use)
Connect Inspector / MCP to:
  http://127.0.0.1:8000/sse/?token=<REDACTED>
If bind fails, FAIL and stop. Do not fall back to Fly.

Allow P0:
- accounts.shopify.com
- partners.shopify.com
- admin.shopify.com
HARD STOP if about:blank or host is www.shopify.com (record HARD_STOP, do not follow marketing).

P0 sequence:
1. tools/list
2. navigate {"url":"https://accounts.shopify.com/"}
3. wait {"delay_ms":8000}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:!!(document.querySelector('[name=cf-turnstile-response],#challenge-form,.cf-turnstile')||/just a moment/i.test(document.title))})"}
5. get_snapshot {"mode":"html"}
6. If cf true: wait 8000 and evaluate again.
7. navigate {"url":"https://partners.shopify.com/"}
8. wait {"delay_ms":3000}
9. evaluate same expression. If host www.shopify.com: HARD_STOP that step, skip admin if you already have cf true on accounts.
10. If accounts cf is false: navigate {"url":"https://admin.shopify.com/"} wait 8000 evaluate.

If hasEmail or hasPassword true and cf false:
  do NOT type credentials (not in this turn).
  record P0 PASS-engine.
  Then P1 only as read-only navigates on
    https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
  evaluate path/host/denied/listVisible. No Save. No staff password.

If still cf true after both waits: verdict FAIL-engine. Not a bounty. Stop. Do not type.

Archive:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
source: local-phantom. server_url: http://127.0.0.1:8000
Verdict PASS-engine | FAIL-engine | HARD_STOP
bounty: false unless P1 shows write on a denied resource (do not expect that this run).

Reply: path, matrix, evaluate JSON, final href. Stop.
