UPDATED: 2026-10-01T13:20Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — H1-6 production storefront primitives

CWD: `/Users/daniele_palagi/Desktop/phantom_cloud`
Production only. Inspector `http://127.0.0.1:6274` already on `https://phantom-cloud-engine.fly.dev`.
Machine `78197e2be34d78` version 166. Do not restart. Do not deploy. Do not edit engine files. Do not use `:8000`.
One SSE. Do not print the token.
Tools only: navigate, get_snapshot, click, type, evaluate, wait.
type: N/A. Do not type a password. Do not open accounts.shopify.com. Do not click a challenge.
Click rule: html `eN` from the snapshot immediately before the click. Do not call get_snapshot ax before that click.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
HARD STOP: about:blank, another merchant, Support, /checkout, /signup, accounts.shopify.com, admin.shopify.com.
If the page is the storefront password gate: verdict GATE. Stop. Do not type.

1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/collections/all"}
3. wait {"delay_ms":2000}
4. get_snapshot {"mode":"html"}
5. evaluate {"expression":"JSON.stringify({href:location.href,path:location.pathname,title:document.title,gate:/password/i.test(location.pathname)||!!document.querySelector('form[action*=password]'),nProduct:document.querySelectorAll('a[href*=\"/products/\"]').length})"}
6. If gate: verdict GATE. Stop.
7. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard"}
8. wait {"delay_ms":2000}
9. get_snapshot {"mode":"html"}
10. evaluate {"expression":"JSON.stringify({href:location.href,title:document.title,status:document.body.innerText.slice(0,400)})"}
11. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard"}
12. wait {"delay_ms":2000}
13. get_snapshot {"mode":"html"}
14. evaluate {"expression":"JSON.stringify({href:location.href,title:document.title,status:document.body.innerText.slice(0,400)})"}
15. Stop. Do not add to cart. Do not click Save.

Verdicts: GATE, PUBLISHED, NOT-FOUND, or PASSWORD. Not a draft unless price or stock contradicts a production admin read. This run has no admin read.

Archive: `runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}`
Redact token. Reply: path, verdict per URL, evaluate JSON. Stop.
