PROJECT: phantom_cloud
UPDATED: 2026-09-28T18:48Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree (Drive phantom_cloud).
Inspector already on https://phantom-cloud-engine.fly.dev
Do not restart. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. One session only.

Task: bound collection + product pages on the owned storefront. Not admin. Not partners. Not cart. Not checkout. Not a full catalog crawl.

Allowlist host: funk-it-up-sdzgxmea.myshopify.com
Allowlist paths:
- / /password (gate only)
- /collections /collections/* 
- /products /products/*
Forbidden: admin.shopify.com, accounts.shopify.com, partners.shopify.com, /admin, any other host, cart, checkout, account, owner “Log in here”.

Hard stop if about:blank OR hostname ≠ funk-it-up-sdzgxmea.myshopify.com OR forbidden host/path.
Do not persist password, emails, phones, or tokens in the archive.

Gate password (owned storefront only, password INPUT only):
bE-4C5TLf)LVmk^

Cap: 1 index + up to 3 collection pages + up to 3 product pages.

1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/collections"}
3. wait {"delay_ms":500}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]')})"}
5. If hasPasswordForm===true AND path is / or /password: same recovery as pages run (html snapshot → type password INPUT e* → html snapshot → click Enter e* → wait 800 → navigate /collections again). Never type into search/contact. Never click owner login.
6. get_snapshot {"mode":"html"}
7. evaluate same expression. Confirm host + path /collections or /collections/*.
8. From that html snapshot only, collect unique same-host hrefs:
   - collection URLs whose path starts with /collections/ and is not /collections
   - product URLs whose path starts with /products/
   Ignore cart, checkout, account, admin, mailto, other hosts.
   If zero collection URLs, navigate /collections/all once, wait 500, snapshot html, evaluate, collect again. That /collections/all visit counts as the index, not as one of the 3 collection pages.
9. Visit in order, each: navigate → wait 500 → get_snapshot html → evaluate:
   - first 3 collection URLs from the list
   - first 3 product URLs from the list (list may grow from collection snapshots; still cap at 3 products total)
10. Stop when caps are hit or lists are exhausted. No extra clicks. No add-to-cart. No type except gate recovery.

Pass if every final href is on-host /collections* or /products*.
Hard stop on foreign host or /admin.

Archive on the device tree only:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Redact token and password.
Reply: path, matrix, evaluate JSON per visited URL, href list. Stop.
