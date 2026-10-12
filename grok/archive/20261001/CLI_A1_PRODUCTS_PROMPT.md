PROJECT: phantom_cloud
UPDATED: 2026-09-28T19:17Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree (Drive phantom_cloud).
Inspector already on https://phantom-cloud-engine.fly.dev
Do not restart. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. One session only.

Task: open up to 3 owned product pages. Collections stay parked. Not cart. Not checkout. Not admin.

Allowlist host: funk-it-up-sdzgxmea.myshopify.com
Allowlist paths: / /password (gate only), /collections/all (index only), /products/*
Forbidden: admin / partners / accounts hosts, /admin, /cart, /checkout, /checkouts, owner Log in, cookie-banner Accept as a destination.

Hard stop if about:blank OR hostname ≠ funk-it-up-sdzgxmea.myshopify.com OR forbidden path/host.
Do not persist password, emails, phones, tokens.

Gate password only if password INPUT on / or /password:
bE-4C5TLf)LVmk^

1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/collections/all"}
3. wait {"delay_ms":500}
4. evaluate page-state:
   JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]')})
5. Gate recovery only if hasPasswordForm===true AND path is / or /password (same type/click Enter as before). Then navigate /collections/all again.
6. evaluate product hrefs (do not use AOM labels; they omit hrefs):
   JSON.stringify([...document.querySelectorAll('a[href*="/products/"]')].map(a=>a.href.split('?')[0]).filter(u=>u.startsWith('https://funk-it-up-sdzgxmea.myshopify.com/products/')).filter((u,i,arr)=>arr.indexOf(u)===i).slice(0,3))
7. If the list is empty: stop. Do not guess handles. Do not click card refs blindly.
8. For each of the up to 3 URLs: navigate → wait 500 → get_snapshot html → evaluate page-state. Confirm path starts with /products/.
9. Stop. No add-to-cart. No checkout. No collection activation.

Pass if 1–3 final hrefs are on-host /products/*.
Hard stop on foreign host or /admin.

Archive: runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Redact token and password.
Reply: path, matrix, href list from step 6, evaluate JSON per PDP. Stop.
