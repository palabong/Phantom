PROJECT: phantom_cloud
UPDATED: 2026-09-30T18:52Z
ENVIRONMENT: Official Grok Build 4.7 High on the device

RESET. Do not apply the old HARD_STOP on www.shopify.com/partners.
Do not use local-chrome operator flow. Do not AppleScript.
All PX run only after MCP Inspector is connected to Phantom SSE.

CWD: /Users/daniele_palagi/Desktop/phantom_cloud
Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED] from PHANTOM_AUTH_TOKEN or Inspector config. Never print. Never write to runs/.

STEP 0 — Inspector first (mandatory)
1. If nothing listens on 127.0.0.1:8000, start local engine:
   PORT=8000 python3 phantom_cloud.py
   Prefer local. Fly https://phantom-cloud-engine.fly.dev is allowed only if local bind fails — record which.
2. Start / attach MCP Inspector to:
   http://127.0.0.1:8000/sse/?token=<REDACTED>
   or Fly /sse/?token=<REDACTED> if local failed.
3. Confirm tools/list returns navigate, get_snapshot, click, type, evaluate, wait.
4. If Inspector is down or tools/list fails: start Inspector. Point it at http://127.0.0.1:8000/sse/?token=<REDACTED> (npx @modelcontextprotocol/inspector or the installed Inspector app). Wait until tools/list returns the 6 tools. Do not stop. Do not drive Chrome outside Inspector. Do not switch to Fly unless :8000 cannot bind.

One SSE session. Six tools. Click by last snapshot ref only.
Do not type passwords this turn (none supplied).
Do not solve Turnstile widgets. If a checkbox/interstitial is visible, wait and re-evaluate; do not click “I am human” solvers.

ALLOWLIST (updated)
- accounts.shopify.com
- partners.shopify.com
- admin.shopify.com
- www.shopify.com ONLY if path starts with /partners or /nl/partners or /de/partners or /it/partners or /en/partners
HARD STOP only on: about:blank, other shops, Support, /checkout, or www.shopify.com outside /partners*.
partners.shopify.com → www.shopify.com/*/partners is ALLOWED. Continue.

P0 (after Inspector is up)
1. tools/list
2. navigate https://accounts.shopify.com/
3. wait 8000
4. evaluate title,href,host,path,hasEmail,hasPassword,cf
   cf = turnstile node OR title matches /just a moment|ci siamo quasi|un moment/i
5. get_snapshot html
6. If cf: wait 8000, evaluate again. Still no type.
7. navigate https://partners.shopify.com/
8. wait 3000
9. evaluate. If redirected to www.shopify.com/*/partners: that is PASS-navigation, not HARD_STOP.
10. If an Iscriviti / Log in / Accedi control is in the last snapshot, click that ref only. Do not fill email.
11. If hasEmail or hasPassword true: P0 PASS-engine. Do not type. Stop this turn after archive.
12. If accounts still cf and partners is only marketing: verdict FAIL-engine on identity, NAV-ok on partners. Not a bounty.

P1 / P2
Only if step 11 is PASS-engine and host is admin.shopify.com or accounts with email field.
Otherwise skip P1/P2 and run P3 on funk-it-up-sdzgxmea.myshopify.com products list from the battery (optional). Do not block the archive on skipped P1.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
source: inspector+local-phantom OR inspector+fly
inspectorConnected: true
hardStop must not fire on www.shopify.com/nl/partners.

Reply: Inspector URL used (no token), path, matrix, evaluate JSON, final href. Stop.
