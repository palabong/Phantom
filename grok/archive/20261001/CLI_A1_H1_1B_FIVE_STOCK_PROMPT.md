PROJECT: phantom_cloud
UPDATED: 2026-10-01T02:20Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Class 4 remeasure. Five handles. Stocks unlocked in the mock store.
20261001T021856Z stopped on /password. Do not stop on the gate. Unlock, then continue the five PDPs.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Click/type ref from the html snapshot immediately before. Never ax for the password field. Never ax for Add.
Do not write the password string into SMOKE, protocol, evaluate, or chat. Archive may say gateUnlocked and pwdLen only.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
ALLOWLIST paths: /password, /products/the-hidden-snowboard, /products/the-archived-snowboard, /products/the-compare-at-price-snowboard, /products/selling-plans-ski-wax, /products/gift-card, /cart
HARD STOP: about:blank OR host ≠ funk-it-up-sdzgxmea.myshopify.com OR /checkout OR admin OR accounts OR another shop.
/password is not a stop. Do not click Log in here, Check out, checkout, cookie Accept/Decline, Buy it now.

GATE (run whenever path is /password, including mid-loop)
1. get_snapshot {"mode":"html"}
2. type on the html INPUT named password (H1-0 had e2). Not e1. Not ax.
   {"ref":"e2","text":"bE-4C5TLf)LVmk^","clear":true}
   If the new snapshot numbers differ, use the current html password INPUT ref.
3. evaluate {"expression":"JSON.stringify({path:location.pathname,pwdLen:(document.querySelector('input[name=password],input[type=password]')||{value:''}).value.length})"}
   pwdLen must be 14. If not, type again with {"ref":"e2","selector":"input[name=password]","text":"bE-4C5TLf)LVmk^","clear":true} and evaluate again.
   If still not 14, evaluate only this and do not log the value:
   {"expression":"(()=>{const i=document.querySelector('input[name=password],input[type=password]');if(!i)return JSON.stringify({set:false,pwdLen:0});i.focus();i.value='bE-4C5TLf)LVmk^';i.dispatchEvent(new Event('input',{bubbles:true}));return JSON.stringify({set:true,pwdLen:i.value.length});})()"}
4. click the html submit BUTTON (H1-0 had e3). Not Log in here.
5. wait {"delay_ms":1500}
6. If path is still /password: evaluate
   {"expression":"(()=>{const i=document.querySelector('input[name=password],input[type=password]');const f=i&&i.form;if(!i||!f)return JSON.stringify({submit:false,pwdLen:(i||{value:''}).value.length});i.value='bE-4C5TLf)LVmk^';f.submit();return JSON.stringify({submit:true,pwdLen:14});})()"}
   wait {"delay_ms":1500}
7. Then navigate the URL that was interrupted. Do not end the run on the gate.

ADD RULE
- After html snapshot, Add is the BUTTON whose name is add.
- Click it only if that button is not labeled Sold out / Esaurito.
- If Sold out: addClicked false, next handle.
- After a click, evaluate /cart before the next PDP.

PDP expression:
{"expression":"JSON.stringify({href:location.href,path:location.pathname,title:document.title,soldOut:/sold out|out of stock|esaurito/i.test(document.body.innerText),price:(document.querySelector('[class*=price]')||{}).textContent||null,addEnabled:!!document.querySelector('button[name=\"add\"]:not([disabled])'),hasPasswordForm:!!document.querySelector('input[type=password]')})"}

Cart expression:
{"expression":"JSON.stringify({href:location.href,path:location.pathname,empty:/your cart is empty|carrello è vuoto/i.test(document.body.innerText),subtotal:(document.body.innerText.match(/€[0-9.,]+/)||[])[0]||null,lineCount:document.querySelectorAll('a[href*=\"/products/\"]').length})"}

Sequence
1. tools/list
2. For each URL below, in order:
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-compare-at-price-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/selling-plans-ski-wax
   https://funk-it-up-sdzgxmea.myshopify.com/products/gift-card
   a. navigate that URL
   b. wait {"delay_ms":800}
   c. If path is /password: run GATE, then navigate this URL again, wait 800
   d. get_snapshot {"mode":"html"}
   e. evaluate PDP expression
   f. If sold out on the add button: skip click. Continue.
   g. Else click the html e-ref of BUTTON name add
   h. wait {"delay_ms":1000}
   i. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/cart"}
   j. wait {"delay_ms":600}
   k. If path is /password: run GATE, then navigate /cart again
   l. evaluate cart expression
3. Final navigate /cart, wait 500, evaluate cart expression once more.

finding true only if a hidden or archived handle produced a payable line (empty false AND subtotal not null), or cart subtotal ≠ PDP price for that handle.
A published in-stock add at the same price is not-a-ticket. Record it.
Do not open /checkout.

PASS-measured: five PDP evaluates recorded on product paths, host stayed A.
FAIL-gate only if GATE ran and path is still /password after step 6. Then archive and stop.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token. No password string in archive files.

SMOKE.md: Target, Server, Sessions, Verdict, Reason, Final href, gateUnlocked, step table.
protocol.json object: source:"inspector+phantom", inspectorConnected:true, finding:true|false, gateUnlocked:true|false, pwdLen:number, handles:[], results[].
evaluate.json object: {pdps:[], cart:{}}.

Reply only: path, verdict, finding true|false, gateUnlocked, evaluate JSON, final href. Stop.
