PROJECT: phantom_cloud
UPDATED: 2026-10-01T11:07Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Class 4 admin status, continued. 20261001T025900Z typed a 22-char address and landed on accounts.shopify.com/signup (Iscriviti). That address is not the tenant.
This run types the tenant alias only. No password. Do not type a password. Do not open signup. Do not create an account.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Do not write the email into SMOKE, protocol, or evaluate. Archive may say emailTyped:true and emailLen.

ALLOWLIST hosts: accounts.shopify.com, admin.shopify.com
ALLOWLIST shop: funk-it-up-sdzgxmea only.
HARD STOP: about:blank OR another merchant OR Support OR /checkout OR path /signup.
Do not click Turnstile. Do not click cookie Accept. Do not click Crea account / Start free trial.

Sequence
1. tools/list
2. navigate {"url":"https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603521722"}
3. wait {"delay_ms":4000}
4. If path is /signup: navigate {"url":"https://accounts.shopify.com/lookup"} and wait 2000.
5. get_snapshot {"mode":"html"}
6. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
7. type into the html email INPUT. Not ax. Selector form is mandatory if the ref leaves the field empty:
   {"selector":"input[type=email],input[name=email],input[name=account]","text":"palabong@wearehackerone.com","clear":true}
8. evaluate {"expression":"JSON.stringify({emailLen:(document.querySelector('input[type=email],input[name=email],input[name=account]')||{value:''}).value.length,path:location.pathname})"}
   emailLen must be 28. If not, type the selector form again and re-evaluate. Do not click Continue until emailLen is 28.
9. Click the html Continue / Next button from the snapshot taken before the click. Not Crea account. wait {"delay_ms":2500}
10. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasPassword:!!document.querySelector('input[type=password]'),hasEmail:!!document.querySelector('input[type=email],input[name=email]'),cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
11. get_snapshot {"mode":"html"}
12. Stop. Do not type a password. If path is /signup, verdict ACCOUNT-MISS, stop.

PASS-email: emailLen 28 and hasPassword true on the next screen.
ACCOUNT-MISS: path /signup or title Iscriviti.
BLOCKED-identity: cf true or no email field.
If the admin product shell loads: record status words for 10323603521722. Do not click Save. Stop.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
mkdir exist_ok=False. Redact email and token.

protocol.json: source:"inspector+phantom", inspectorConnected:true, emailTyped:true|false, emailLen:number, hasPassword:true|false, finding:false, results[].
evaluate.json object. No email string.

Reply only: path, verdict, emailLen, hasPassword, evaluate JSON, final href. Stop.
