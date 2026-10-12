PROJECT: phantom_cloud
UPDATED: 2026-09-28T19:31Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Inspector on https://phantom-cloud-engine.fly.dev
Do not restart/deploy/edit engine. Token → [REDACTED]. One session.

Task R1: live collections only. Not products. Not cart.

Host: funk-it-up-sdzgxmea.myshopify.com
Allow: / /password (gate), /collections, /collections/*
Forbid: admin/partners/accounts, /admin, /cart, /checkout, /products, Log in.

Hard stop if about:blank or host mismatch.
Do not archive password/token/email/phone.

Gate password (password INPUT on / or /password only): bE-4C5TLf)LVmk^

1. tools/list
2. navigate https://funk-it-up-sdzgxmea.myshopify.com/collections
3. wait 500
4. evaluate page-state JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]')})
5. Gate recovery if needed, then navigate /collections again.
6. get_snapshot html
7. evaluate collection hrefs:
   JSON.stringify([...document.querySelectorAll('a[href*="/collections/"]')].map(a=>a.href.split('?')[0]).filter(u=>u.startsWith('https://funk-it-up-sdzgxmea.myshopify.com/collections/')&&!u.endsWith('/collections')&&!u.endsWith('/collections/all')&&!u.includes('/products/')).filter((u,i,arr)=>arr.indexOf(u)===i).slice(0,3))
8. If empty: evaluate the same on innerText names only, then stop. Do not invent handles.
9. For each URL (max 3): navigate → wait 500 → get_snapshot html → evaluate page-state plus:
   JSON.stringify({path:location.pathname,productLinks:[...document.querySelectorAll('a[href*="/products/"]')].map(a=>a.href.split('?')[0]).filter((u,i,arr)=>arr.indexOf(u)===i).slice(0,5),countText:(document.body.innerText.match(/\d+\s+products?/i)||[])[0]||null})
10. Stop.

Pass: each final href is on-host /collections/*.
Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Reply: path, matrix, collection hrefs, per-page evaluate. Stop.
