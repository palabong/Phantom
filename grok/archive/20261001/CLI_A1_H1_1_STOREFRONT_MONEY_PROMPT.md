PROJECT: phantom_cloud
UPDATED: 2026-10-01T00:17Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector. Do not AppleScript.

H1-0b 20261001T001432Z PASS-engine. Storefront A is unlocked in that Chrome.
This run is the ticket-class measurement on that session: storefront price / stock / publish vs what a buyer can do.
Not admin. Not accounts. Not a second store.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Click/type ref from the snapshot immediately before. Never CSS "a, button".
type: N/A. No password this run. If the gate returns, stop. Do not retype a password.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
ALLOWLIST paths: /, /collections, /collections/all, /products/*, /cart, /search
HARD STOP: about:blank OR host ≠ funk-it-up-sdzgxmea.myshopify.com OR /password OR admin.shopify.com OR accounts.shopify.com OR partners.shopify.com OR /checkout OR Support OR another shop.
Do not click Log in, Log in here, Check out, checkout, cookie Accept/Decline.

Finding-candidate only if money changes:
- a hidden, archived, or unpublished handle is addable at a price > 0, or
- cart line price ≠ PDP price, or
- sold-out PDP still adds a payable line.
OOS test SKUs that stay OOS, and hidden-by-URL that cannot be added, are not a ticket. Record them.

Sequence
1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/collections/all"}
3. wait {"delay_ms":800}
4. If href path is /password: verdict FAIL-session, archive, stop.
5. get_snapshot {"mode":"html"}
6. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),oos:(document.body.innerText.match(/Out of stock \\((\\d+)\\)/)||[])[1]||null,instock:(document.body.innerText.match(/In stock \\((\\d+)\\)/)||[])[1]||null,cardIds:[...document.querySelectorAll('[id*=\"product-grid-\"]')].map(n=>(n.id.match(/(\\d{8,})$/)||[])[1]).filter(Boolean).slice(0,8),webdriver:navigator.webdriver===true})"}
7. For each URL, navigate, wait 600, evaluate the PDP expression, get_snapshot html:
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-compare-at-price-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/selling-plans-ski-wax
   https://funk-it-up-sdzgxmea.myshopify.com/products/gift-card
   PDP expression:
   {"expression":"JSON.stringify({href:location.href,path:location.pathname,title:document.title,status:document.querySelector('title')?document.title:null,price:(document.querySelector('[class*=price]')||{}).textContent||null,soldOut:/sold out|out of stock|esaurito/i.test(document.body.innerText),addEnabled:!!document.querySelector('button[name=\"add\"]:not([disabled]),form[action*=\"/cart/add\"] button:not([disabled])'),hasPasswordForm:!!document.querySelector('input[type=password]')})"}
   If path is /password: HARD-ish stop as FAIL-session. Do not continue.
   If addEnabled true: get_snapshot html, click the add button ref from THAT snapshot (not cookie, not checkout, not Log in), wait 800, navigate /cart, wait 500, evaluate:
   {"expression":"JSON.stringify({href:location.href,path:location.pathname,cartText:document.body.innerText.slice(0,400),lineCount:document.querySelectorAll('[href*=\"/products/\"]').length})"}
   Then navigate back. Do not open /checkout.
8. After the five PDPs, navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/cart"}
9. wait {"delay_ms":500}
10. evaluate {"expression":"JSON.stringify({href:location.href,path:location.pathname,empty:/your cart is empty|carrello è vuoto/i.test(document.body.innerText),subtotal:(document.body.innerText.match(/€[0-9.,]+/)||[])[0]||null})"}

PASS-measured: five PDP evaluates recorded, host stayed A, no /checkout.
finding-candidate: addEnabled true on hidden/archived OR cart subtotal > 0 after an OOS add. Stop. Do not pivot.
not-a-ticket: all five OOS or 404, addEnabled false, cart empty. Class closed for this session.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token. No password string.

SMOKE.md: Target, Server, Sessions, Verdict, Reason, Final href, step table.
protocol.json object: source:"inspector+phantom", inspectorConnected:true, finding:true|false, pdps:[], cartEmpty:true|false, results[].
evaluate.json object. One object with keys gate, catalog, pdps[], cart.

Reply only: path, verdict, finding true|false, evaluate JSON, final href. Stop.
