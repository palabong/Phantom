PROJECT: phantom_cloud
UPDATED: 2026-09-28T20:53Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Inspector on https://phantom-cloud-engine.fly.dev
Do not restart/deploy/edit engine. Token → [REDACTED]. One session.

Task R3: one add-to-cart on a pinned owned PDP, then /cart. Do not fill cards. Do not type 1/2/3.

Pinned PDP:
https://funk-it-up-sdzgxmea.myshopify.com/products/the-collection-snowboard-hydrogen

Host: funk-it-up-sdzgxmea.myshopify.com
Allow:
- / /password (gate only)
- /products/the-collection-snowboard-hydrogen
- /cart
- /checkout /checkouts/* only if the theme redirects after add (do not click checkout)
Forbid: other /products/*, /collections/*, admin/partners/accounts, /admin, PCI, Log in, gift-card, 3p-fulfilled.

Hard stop if about:blank or host mismatch.
Do not archive password/token/email/phone/PAN.
Gate: bE-4C5TLf)LVmk^ on password INPUT only.

1. tools/list
2. navigate https://funk-it-up-sdzgxmea.myshopify.com/products/the-collection-snowboard-hydrogen
3. wait 500
4. evaluate JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),hasAddToCart:!!document.querySelector('form[action*="/cart/add"],button[name=add]')})
5. If hasPasswordForm===true AND path is / or /password: gate recovery (html → type password INPUT → html → click Enter → wait 800) then navigate the pinned PDP again. Never type into search/contact.
6. get_snapshot html
7. Confirm path is /products/the-collection-snowboard-hydrogen. Else hard stop.
8. click Add only if THIS html snapshot has a clear add control (name=add, text Add / Add to cart, form /cart/add). If sold out and no add: evaluate {soldOut:true,added:false} and skip to step 10 with N/A click. Do not click Checkout on the PDP.
9. wait 800
10. navigate https://funk-it-up-sdzgxmea.myshopify.com/cart
11. wait 500 → get_snapshot html → evaluate
    JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasCheckout:!!document.querySelector('button[name=checkout],a[href*="checkout"],button[type=submit]'),empty:/empty/i.test(document.body.innerText)})
12. Do not click checkout. Do not type payment fields.

Pass: final host allowlisted; path /cart (or documented theme equivalent). Click N/A + empty cart is PASS-with-note if Add was absent.
Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Reply: path, matrix, PDP evaluate, cart evaluate. Stop.
