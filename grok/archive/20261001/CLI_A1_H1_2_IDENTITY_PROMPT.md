PROJECT: phantom_cloud
UPDATED: 2026-10-01T00:25Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build — MCP Inspector already running

CWD: device production tree (Drive phantom_cloud).
Stay on the existing Inspector SSE: http://127.0.0.1:8000/sse/
Token already in Inspector. Never print it. Never write it to runs/.
Do not start a second Inspector or SSE. Do not fly deploy. Do not edit engine files.
Do not drive Chrome outside Inspector.

H1-1 20261001T002138Z closed class 4 (storefront money). not-a-ticket.
This run opens classes 1–3. Prerequisite only: can Phantom reach an email/password form on accounts or admin for store A.
No password supplied this turn. type = N/A. Do not invent a secret.

Tools only: navigate, get_snapshot, click, type, evaluate, wait.
Click ref from the snapshot immediately before. Never CSS "a, button".
Do not click Turnstile, hCaptcha, “I am human”, cookie Accept/Decline, Support.

ALLOWLIST hosts: accounts.shopify.com, admin.shopify.com, partners.shopify.com
ALLOWLIST shop after redirect: funk-it-up-sdzgxmea only.
HARD STOP: about:blank OR another merchant OR /checkout OR Support OR www.shopify.com outside /partners*.
partners.shopify.com → www.shopify.com/*/partners is allowed. Continue.

Sequence
1. tools/list
2. navigate {"url":"https://accounts.shopify.com/lookup?redirect=https%3A%2F%2Fadmin.shopify.com%2Fstore%2Ffunk-it-up-sdzgxmea"}
3. wait {"delay_ms":8000}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:!!(document.querySelector('[name=cf-turnstile-response],#challenge-form,.cf-turnstile')||/just a moment|ci siamo quasi|un moment/i.test(document.title)),webdriver:navigator.webdriver===true})"}
5. get_snapshot {"mode":"html"}
6. If cf true: wait {"delay_ms":8000}, evaluate the same expression again. Do not click the checkbox.
7. If hasEmail or hasPassword is true: stop. Verdict PASS-engine. Do not type.
8. If still cf and no email field: navigate {"url":"https://admin.shopify.com/store/funk-it-up-sdzgxmea"}
9. wait {"delay_ms":5000}
10. evaluate the same expression
11. get_snapshot {"mode":"ax"}
12. If an Accedi / Log in / Continue control is in the last snapshot and it is not cookie Accept: click that ref only. wait 2000. evaluate again.
13. Do not fill email. Do not type.

PASS-engine: hasEmail or hasPassword true and cf false. Identity form is reachable. Stop for the secret.
FAIL-engine: cf true after both waits, or no email/password field. Not a bounty. Classes 1–3 stay blocked on this pipe until a later run clears cf.
HARD_STOP: about:blank, other shop, Support.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
mkdir exist_ok=False. Redact token. No passwords.

SMOKE.md: Target, Server, Sessions, Verdict, Reason, Final href, step table.
protocol.json object: source:"inspector+phantom", inspectorConnected:true, cf:true|false, hasEmail:true|false, hasPassword:true|false, results[].
evaluate.json object.

Reply only: path, verdict, evaluate JSON, final href. Stop.
