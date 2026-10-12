PROJECT: phantom_cloud
UPDATED: 2026-10-01T02:34Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Class 4 only. 20261001T023038Z clicked Add to cart on hidden and archived and got lineCount 0.
This run must submit the product form, not only click. Two handles only.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Do not write the password string into SMOKE, protocol, evaluate, or chat.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
ALLOWLIST paths: /password, /products/the-hidden-snowboard, /products/the-archived-snowboard, /cart
HARD STOP: about:blank OR host ≠ funk-it-up-sdzgxmea.myshopify.com OR /checkout OR admin OR accounts OR another shop.
/password is not a stop. Do not click Log in here, Check out, cookie Accept/Decline, Buy it now.

GATE if path is /password
1. get_snapshot {"mode":"html"}
2. type {"ref":"e2","text":"bE-4C5TLf)LVmk^","clear":true} on the html password INPUT. Not ax.
3. evaluate {"expression":"JSON.stringify({pwdLen:(document.querySelector('input[name=password],input[type=password]')||{value:''}).value.length,path:location.pathname})"}
   If pwdLen !== 14, type again with selector input[name=password], same text.
4. click html submit BUTTON e3, not Log in here. wait {"delay_ms":1500}
5. If still /password, evaluate {"expression":"(()=>{const i=document.querySelector('input[name=password],input[type=password]');const f=i&&i.form;if(!i||!f)return JSON.stringify({submit:false});i.value='bE-4C5TLf)LVmk^';f.submit();return JSON.stringify({submit:true,pwdLen:i.value.length});})()"}
   wait {"delay_ms":1500}
6. Navigate the interrupted URL. Continue.

For each URL:
https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard
https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard
1. navigate, wait 800. If /password, GATE, then navigate again.
2. get_snapshot {"mode":"html"}
3. evaluate {"expression":"JSON.stringify({href:location.href,path:location.pathname,title:document.title,soldOut:/sold out|esaurito/i.test(document.body.innerText),variant:(document.querySelector('input[name=\"id\"],select[name=\"id\"]')||{}).value||null,price:(document.querySelector('[class*=price]')||{}).textContent||null})"}
4. Submit the cart form. Do not click Buy it now. evaluate:
   {"expression":"(()=>{const f=document.querySelector('form[action*=\"/cart/add\"]');if(!f)return JSON.stringify({submit:false,path:location.pathname});f.submit();return JSON.stringify({submit:true,action:f.getAttribute('action')});})()"}
5. wait {"delay_ms":1500}
6. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/cart"}
7. wait {"delay_ms":600}
8. If /password, GATE, then navigate /cart again.
9. evaluate {"expression":"JSON.stringify({href:location.href,path:location.pathname,empty:/your cart is empty|carrello è vuoto/i.test(document.body.innerText),subtotal:(document.body.innerText.match(/\\$[0-9.,]+|€[0-9.,]+/)||[])[0]||null,lineCount:document.querySelectorAll('a[href*=\"/products/\"]').length,body:document.body.innerText.slice(0,500)})"}

finding true only if hidden or archived produced empty false AND subtotal not null.
Same-price published add is not-a-ticket. A hidden or archived payable line is finding-candidate. Stop. Do not checkout.

PASS-measured: both handles recorded, host stayed A.
FAIL-gate only if still /password after GATE step 5.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
mkdir exist_ok=False. No password string in archive files.

protocol.json: source:"inspector+phantom", inspectorConnected:true, finding:true|false, gateUnlocked:true|false, handles:[], results[].
evaluate.json object: {pdps:[], cart:{}}.

Reply only: path, verdict, finding true|false, evaluate JSON, final href. Stop.
