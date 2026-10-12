PROJECT: phantom_cloud
UPDATED: 2026-10-01T02:49Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Class 4 admin status, continued. 20261001T024644Z is on accounts.shopify.com/lookup. hasEmail true. hasPassword true. cf false.
This turn supplies the email only. No password. Do not type a password. Do not invent one.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Do not write the email or any password into SMOKE, protocol, or evaluate. Archive may say emailTyped:true.

ALLOWLIST hosts: accounts.shopify.com, admin.shopify.com
ALLOWLIST shop after login: funk-it-up-sdzgxmea only.
HARD STOP: about:blank OR another merchant OR Support OR /checkout.
Do not click Turnstile. Do not click cookie Accept.

Sequence
1. tools/list
2. navigate {"url":"https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603521722"}
3. wait {"delay_ms":4000}
4. get_snapshot {"mode":"html"}
5. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
6. If hasEmail: type into the html email INPUT ref from step 4 (not ax):
   {"ref":"<e-ref of email INPUT>","text":"palabong@hackerone.com","clear":true}
   If the snapshot has no e-ref, use {"selector":"input[type=email],input[name=email],input[name=account]","text":"palabong@hackerone.com","clear":true}
7. evaluate {"expression":"JSON.stringify({emailLen:(document.querySelector('input[type=email],input[name=email],input[name=account]')||{value:''}).value.length})"}
   emailLen must be 23. If not, type again with the selector form above.
8. Click the html Continue / Next / Accedi button from the snapshot that is not cookie Accept. wait {"delay_ms":2500}
9. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasPassword:!!document.querySelector('input[type=password]'),hasEmail:!!document.querySelector('input[type=email],input[name=email]'),cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
10. get_snapshot {"mode":"html"}
11. Stop. Do not type a password.

PASS-email: emailLen 23 and the next screen is recorded (password field or admin shell).
BLOCKED-identity: cf true or email field missing.
If admin product shell loads without a password prompt: record status words for product 10323603521722 only. Do not click Save. Then stop.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
mkdir exist_ok=False. Redact email and token.

protocol.json: source:"inspector+phantom", inspectorConnected:true, emailTyped:true|false, emailLen:number, hasPassword:true|false, finding:false, results[].
evaluate.json object. No email string.

Reply only: path, verdict, emailLen, hasPassword, evaluate JSON, final href. Stop.
