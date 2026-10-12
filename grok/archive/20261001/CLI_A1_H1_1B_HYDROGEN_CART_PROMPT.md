PROJECT: phantom_cloud
UPDATED: 2026-10-01T00:39Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Class 4 only. Previous five handles were sold out. This run uses the in-stock PDP named this turn.
Do not open the-hidden-snowboard, the-archived-snowboard, the-compare-at-price-snowboard, selling-plans-ski-wax, gift-card.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Click ref from the snapshot immediately before. Never CSS "a, button".
type: N/A. No password. If path becomes /password: FAIL-session, archive, stop.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
ALLOWLIST paths: /products/the-collection-snowboard-hydrogen, /cart
HARD STOP: about:blank OR host ≠ funk-it-up-sdzgxmea.myshopify.com OR /password OR /checkout OR admin OR accounts OR another shop.
Do not click Log in, Check out, checkout, cookie Accept/Decline.

Target: https://funk-it-up-sdzgxmea.myshopify.com/products/the-collection-snowboard-hydrogen

Sequence
1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/products/the-collection-snowboard-hydrogen"}
3. wait {"delay_ms":800}
4. get_snapshot {"mode":"html"}
5. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),soldOut:/sold out|out of stock|esaurito/i.test(document.body.innerText),price:(document.querySelector('[class*=price]')||{}).textContent||null,addEnabled:!!document.querySelector('button[name=\"add\"]:not([disabled]),form[action*=\"/cart/add\"] button:not([disabled])'),webdriver:navigator.webdriver===true})"}
6. If path is /password: stop FAIL-session.
7. If addEnabled false: verdict not-a-ticket, archive, stop. Do not click.
8. From the step-4 html snapshot, click the add control whose name is add (button[name=add] mapped to an e-ref). Not Accept. Not checkout.
9. wait {"delay_ms":1000}
10. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/cart"}
11. wait {"delay_ms":600}
12. get_snapshot {"mode":"html"}
13. evaluate {"expression":"JSON.stringify({href:location.href,path:location.pathname,empty:/your cart is empty|carrello è vuoto/i.test(document.body.innerText),hasHydrogen:/hydrogen|collection snowboard/i.test(document.body.innerText),subtotal:(document.body.innerText.match(/€[0-9.,]+/)||[])[0]||null,qty:(document.querySelector('input[name=\"updates[]\"],input[name*=\"quantity\"]')||{}).value||null})"}

finding true only if the cart has a payable line (empty false AND subtotal not null) for this product.
In-stock add of a published test SKU with matching cart price is not-a-ticket. Record it. Do not open checkout.

PASS-measured: PDP and cart evaluates recorded, host stayed A.
FAIL-session: /password or host left allowlist.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token.

SMOKE.md: Target, Server, Sessions, Verdict, Reason, Final href, step table.
protocol.json object: source:"inspector+phantom", inspectorConnected:true, finding:true|false, addRef:"", results[].
evaluate.json object with keys pdp, cart.

Reply only: path, verdict, finding true|false, evaluate JSON, final href. Stop.
