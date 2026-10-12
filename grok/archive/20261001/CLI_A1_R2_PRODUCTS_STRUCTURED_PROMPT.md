PROJECT: phantom_cloud
UPDATED: 2026-09-28T19:31Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Inspector on https://phantom-cloud-engine.fly.dev
Do not restart/deploy/edit engine. Token → [REDACTED]. One session.

Task R2: three PDPs with structured evaluate (AOM-worthy payload). Not cart submit. Not checkout.

Host: funk-it-up-sdzgxmea.myshopify.com
Allow: / /password (gate), /collections/all (discover only), /products/*
Forbid: admin/partners/accounts, /admin, /cart, /checkout, Log in.

Hard stop if about:blank or host mismatch.
Do not archive password/token/email/phone.

Gate: bE-4C5TLf)LVmk^ on password INPUT only.

1. tools/list
2. navigate https://funk-it-up-sdzgxmea.myshopify.com/collections/all
3. wait 500
4. page-state evaluate (same as R1). Gate recovery if needed, re-open /collections/all.
5. evaluate hrefs:
   JSON.stringify([...document.querySelectorAll('a[href*="/products/"]')].map(a=>a.href.split('?')[0]).filter(u=>u.startsWith('https://funk-it-up-sdzgxmea.myshopify.com/products/')).filter((u,i,arr)=>arr.indexOf(u)===i).slice(0,3))
6. Empty list → stop. No guessed handles. No blind card clicks.
7. For each of up to 3 URLs:
   navigate → wait 500 → get_snapshot html → get_snapshot ax → evaluate
   JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),hasAddToCart:!!document.querySelector('form[action*="/cart/add"],button[name=add],button[type=submit]'),availability:(document.body.innerText.match(/sold out|out of stock|in stock|unavailable/i)||[])[0]||null,price:(document.querySelector('[class*=price]')||{}).textContent||null,variantInputs:[...document.querySelectorAll('input[name^=id],select[name^=id],input[name=id]')].map(el=>({tag:el.tagName,name:el.name,value:(el.value||'').slice(0,24)})).slice(0,4)})
8. Stop. Do not click Add to cart.

Pass: 1–3 on-host /products/*.
Archive runs/prod_postdeploy_<UTC>/…
Reply: path, matrix, 3 hrefs, 3 evaluate JSON. Stop.
