UPDATED: 2026-10-01T13:12Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — H1-1g production, other method only

CWD: `/Users/daniele_palagi/Desktop/phantom_cloud`
Production only. Inspector `http://127.0.0.1:6274` already on `https://phantom-cloud-engine.fly.dev`.
Machine `78197e2be34d78` version 166. Do not restart. Do not deploy. Do not edit engine files. Do not use `:8000`.
One SSE. Do not print the token.
Tools only: navigate, get_snapshot, click, type, evaluate, wait.
type: N/A. Do not type. Do not approve a passkey. Do not create an account.
Click rule: html `eN` from the snapshot immediately before the click. Do not call get_snapshot ax before that click.

ALLOWLIST: accounts.shopify.com, admin.shopify.com, funk-it-up-sdzgxmea.myshopify.com
HARD STOP: about:blank, another merchant, Support, /checkout, /signup.
Do not click Turnstile, cookie Accept, chiave di accesso, passkey, Crea account.

1. tools/list
2. navigate {"url":"https://accounts.shopify.com/login"}
3. wait {"delay_ms":2000}
4. get_snapshot {"mode":"html"}
5. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasPassword:!!document.querySelector('input[type=password]'),cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
6. If path is /signup: verdict ACCOUNT-MISS. Stop.
7. Click the html e-ref whose text is Accedi con un altro metodo or Sign in with another method. Not the passkey control. wait {"delay_ms":2000}
8. get_snapshot {"mode":"html"}
9. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasPassword:!!document.querySelector('input[type=password]'),passwordCount:document.querySelectorAll('input[type=password]').length,cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
10. Stop. Do not type.

PASS-password-field: hasPassword true.
STILL-PASSKEY: passkey screen remains.
If the admin product shell loads, record status words only. Do not click Save.

Archive: `runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}`
Redact token and email. Reply: path, verdict, evaluate JSON. Stop.
