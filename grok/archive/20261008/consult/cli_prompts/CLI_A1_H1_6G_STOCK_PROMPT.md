UPDATED: 2026-10-07T00:04Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — H1-6g stock read only

Paste into the device Grok Build terminal. Continues H1-6f. Not a draft slice.

```
CWD: "/Users/daniele_palagi/Desktop/phantom_cloud 2"

H1-6g. Production storefront only. Store funk-it-up-sdzgxmea.myshopify.com. Session was unlocked at 20261001T135742Z. H1-6f already read hidden $749.95 and archived $629.95. stock false was a regex miss, not a stock reading. This slice reads availability only.

Do not open http://127.0.0.1:6274. Do not write a Python client. Do not run smoke_test.py or execute_task.py. Do not edit phantom_cloud.py, Dockerfile, fly.toml, or requirements.txt. Do not fly deploy. Do not restart machine 78197e2be34d78. Do not print a token. Do not type. Do not add to cart. Do not open accounts, admin, checkout, or signup. Do not contact Support. If the page is /password, verdict GATE and stop. If about:blank or another merchant, stop.

Use only `npx --yes @modelcontextprotocol/inspector --cli "<sse url from /private/tmp/phantom-inspector.log>" --transport sse --format json`. If --transport sse is rejected, stop and quote the error. Time every call. Click only a Decline button, and only with the eN from the html snapshot immediately before that click.

1. tools/list
2. navigate url=https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard
3. wait delay_ms=2000
4. get_snapshot mode=html
5. If the snapshot has a Decline button, click that eN, then wait delay_ms=1000 and get_snapshot mode=html
6. evaluate expression=JSON.stringify({href:location.href,title:document.title,price:(document.body.innerText.match(/\$[0-9]+\.[0-9]{2}/)||[])[0]||null,available:(window.meta&&window.meta.product&&window.meta.product.variants)?window.meta.product.variants.map(v=>({id:v.id,available:v.available,inventory:v.inventory_quantity??null})):null,text:document.body.innerText.replace(/\s+/g,' ').slice(0,400)})
7. navigate url=https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard
8. wait delay_ms=2000
9. get_snapshot mode=html
10. evaluate with the same expression
11. Stop.

Public price plus available on a test-data title is not a draft. No admin read.
Archive under runs/prod_postdeploy_<UTC>/ as SMOKE.md, protocol.json, html_snapshot.txt, evaluate.json. Redact tokens. SMOKE.md columns: Step / Tool, Result, Latency, Details.
Reply: path, both evaluate JSON, available values. Stop.
```
