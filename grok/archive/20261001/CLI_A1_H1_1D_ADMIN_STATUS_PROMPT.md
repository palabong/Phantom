PROJECT: phantom_cloud
UPDATED: 2026-10-01T12:01Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

INTEGRAL MCP PATH (mandatory, do not skip a hop)
CLI operator
→ MCP Inspector already running in this terminal (do not start a second Inspector)
→ existing SSE session http://127.0.0.1:8000/sse/?token=<already in Inspector>
→ Phantom Cloud local engine (nodriver, headless=False on Xvfb)
→ exactly these six tools, in calls, never via desktop Chrome, AppleScript, or the address bar:
   tools/list
   navigate
   get_snapshot
   click
   type
   evaluate
   wait

Token never printed. Never written to runs/.
Do not start a second SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

Rewind. Login page is https://admin.shopify.com/login only.
Do not type on accounts.shopify.com. Do not follow a passkey screen there.
No password this turn. Do not type a password. Do not approve a passkey.

ALLOWLIST hosts: admin.shopify.com, partners.shopify.com, accounts.shopify.com
Login host: admin.shopify.com only.
ALLOWLIST shop: funk-it-up-sdzgxmea only.
HARD STOP: about:blank OR another merchant OR Support OR /checkout OR /signup.
If host becomes accounts.shopify.com: do not type, do not click. Call navigate back to https://admin.shopify.com/login.
Do not click Turnstile or cookie Accept.

Ids:
- the-hidden-snowboard 10323603521722
- the-archived-snowboard 10323603259578

Calls, in order. Each bullet is one MCP tool call.
1. tools/list
2. navigate {"url":"https://admin.shopify.com/login"}
3. wait {"delay_ms":3000}
4. evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:/just a moment|ci siamo quasi/i.test(document.title)})"}
5. If host is accounts.shopify.com: navigate {"url":"https://admin.shopify.com/login"} then wait {"delay_ms":3000} then evaluate the same expression. Do not type on accounts.
6. get_snapshot {"mode":"html"}
7. If hasEmail and host is admin.shopify.com: type {"selector":"input[type=email],input[name=email],input[name=account]","text":"palabong@wearehackerone.com","clear":true}
8. evaluate {"expression":"JSON.stringify({emailLen:(document.querySelector('input[type=email],input[name=email],input[name=account]')||{value:''}).value.length,host:location.hostname})"}
   emailLen must be 28. If not, repeat call 7 and call 8. Do not click before 28.
9. get_snapshot {"mode":"html"}
10. click {"ref":"<e-ref of Continue on that html snapshot>"}
11. wait {"delay_ms":2500}
12. evaluate the call-4 expression
13. Stop if hasPassword true, or if the admin shell for funk-it-up-sdzgxmea is visible. Do not type a password.
14. If the admin shell is open: navigate {"url":"https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603521722"} then wait {"delay_ms":3000} then get_snapshot {"mode":"html"} then evaluate {"expression":"JSON.stringify({href:location.href,host:location.hostname,path:location.pathname,title:document.title,status:/archived|draft|active|unlisted|unpublished|non pubblicato|bozza|archiviato/i.exec(document.body.innerText||'')})"}
15. navigate {"url":"https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603259578"} then wait {"delay_ms":3000} then get_snapshot {"mode":"html"} then evaluate the same expression. Do not click Save.

PASS-admin-login: host stayed admin.shopify.com and emailLen 28 or the admin shell loaded.
PASS-password-field: password field on admin.shopify.com. Stop.
BLOCKED-redirect: still on accounts.shopify.com after the return navigate.
finding true only if admin status is archived, draft, or not on Online Store. Otherwise finding false.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
mkdir exist_ok=False. Redact email and token.

protocol.json: source:"inspector+phantom", mcpPath:"Inspector→127.0.0.1:8000/sse→six tools", inspectorConnected:true, loginHost:"admin.shopify.com", emailLen:number, hasPassword:true|false, finding:true|false, results[].
evaluate.json object. No email string.

Reply only: path, verdict, loginHost, emailLen, hasPassword, evaluate JSON, final href. Stop.
