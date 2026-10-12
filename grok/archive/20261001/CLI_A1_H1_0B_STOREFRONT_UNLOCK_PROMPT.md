PROJECT: phantom_cloud
UPDATED: 2026-10-01T00:13Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Server: http://127.0.0.1:8000/sse/  (token already in Inspector — never print, never write to runs/).
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
This run: unlock the storefront gate, then open /collections/all.

ALLOWLIST host: funk-it-up-sdzgxmea.myshopify.com
ALLOWLIST paths: /password, /, /collections, /collections/all, /products, /pages, /search, /cart
HARD STOP: about:blank OR host ≠ funk-it-up-sdzgxmea.myshopify.com OR admin/accounts/partners OR Support OR /checkout OR another shop.

Do not click e4 or any “Log in here” link.
Do not write the password string into SMOKE, protocol, evaluate, or chat.
Archive may record passwordTyped, pwdLen, unlocked only.

TYPE RULE (do not improvise)
- After html snapshot, the password field is [e2: INPUT 'password'].
- type MUST use ref e2. Never ax13. Never ax*. Never e1 (authenticity_token). Never e4.
- Submit MUST use ref e3 (html BUTTON). Never ax14 unless e3 is missing from the same html snapshot.
- If the new html snapshot numbers differ, use the INPUT whose name/label is password, still html e-ref, not ax.

Sequence
1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/password"}
3. wait {"delay_ms":800}
4. get_snapshot {"mode":"html"}
5. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),pwdLen:(document.querySelector('input[type=password],input[name=password]')||{value:''}).value.length,webdriver:navigator.webdriver===true})"}
6. type EXACTLY:
   {"ref":"e2","text":"bE-4C5TLf)LVmk^","clear":true}
   If step 4 html snapshot has no e2 password INPUT, use {"ref":"<current html password INPUT ref>","text":"bE-4C5TLf)LVmk^","clear":true}. Still not ax.
7. evaluate the same expression as step 5. pwdLen must be 14. If pwdLen !== 14:
   type again {"ref":"e2","selector":"input[name=password]","text":"bE-4C5TLf)LVmk^","clear":true}
   evaluate again. If still !== 14: evaluate ONLY this (do not log the value):
   {"expression":"(()=>{const i=document.querySelector('input[name=password],input[type=password]');if(!i)return JSON.stringify({set:false,pwdLen:0});i.focus();i.value='bE-4C5TLf)LVmk^';i.dispatchEvent(new Event('input',{bubbles:true}));i.dispatchEvent(new Event('change',{bubbles:true}));return JSON.stringify({set:true,pwdLen:i.value.length});})()"}
8. click {"ref":"e3"}
9. wait {"delay_ms":2000}
10. evaluate step-5 expression
11. If path is still /password: evaluate
    {"expression":"(()=>{const i=document.querySelector('input[name=password],input[type=password]');const f=i&&i.form;if(!i||!f)return JSON.stringify({submit:false,path:location.pathname,pwdLen:(i||{value:''}).value.length});i.value='bE-4C5TLf)LVmk^';f.submit();return JSON.stringify({submit:true,pwdLen:14});})()"}
    wait {"delay_ms":2000}
    evaluate step-5 expression
12. If path is not /password: navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/collections/all"}
13. wait {"delay_ms":800}
14. get_snapshot {"mode":"html"}
15. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),nProductLinks:document.querySelectorAll('a[href*=\"/products/\"]').length,webdriver:navigator.webdriver===true})"}

PASS-engine: host A, final path ≠ /password, hasPasswordForm false, catalog evaluate object.
FAIL-gate: still /password after step 11. Record final pwdLen. Not a bounty.
FAIL-engine: no six tools, about:blank, host leaves allowlist.
HARD_STOP: Log in here clicked or admin/accounts loaded.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token. No password string in archive files.

SMOKE.md: Target, Server, Sessions, Verdict, Reason, Final href, pwdLen, unlocked, step table.
protocol.json object: source:"inspector+phantom", inspectorConnected:true, passwordTyped:true|false, pwdLen:number, unlocked:true|false, typeRef:"e2"|other, submitRef:"e3"|other, results[].
evaluate.json object (not a string). Never include the password value.

Reply only: path, verdict, unlocked, pwdLen, typeRef, submitRef, evaluate JSON, final href. Stop.
