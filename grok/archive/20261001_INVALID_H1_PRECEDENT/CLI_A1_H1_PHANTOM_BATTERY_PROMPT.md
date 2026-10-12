PROJECT: phantom_cloud
UPDATED: 2026-09-30T09:02Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build / Antigravity — execute ONLY through Phantom Cloud MCP

HOW TO RUN
CWD: device production tree (Drive phantom_cloud).
Connect the Inspector / MCP client to:
  https://phantom-cloud-engine.fly.dev
Use the existing SSE session. Token from env or ~/.mcp-inspector — never print it, never write it to runs/.
Do not start a second session. MAX_CONCURRENT_SESSIONS = 1.
Do not use local Chrome. Do not use AppleScript / Accessibility.
Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Tools only: tools/list, navigate, wait, get_snapshot, evaluate, click, type.
Click uses {"ref":"eN"|"axN"} from the last snapshot. Never CSS "a, button".
type only if this prompt says so AND the user supplied a secret in the same turn. This battery does not supply passwords.

Archive each part as its own dir:
  runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
  add html_snapshot.txt only if you took html.
mkdir exist_ok=False. Redact token, emails, phones, passwords.
evaluate.json must be an object. SMOKE.md must have Verdict, Reason, step table.

HARD STOP if location is about:blank OR hostname is not in that part’s allowlist.
Do not Support. Do not PCI. Do not other merchants.

If after navigate+wait the page is Cloudflare / hCaptcha / Accedi / Just a moment...:
  record cf=true, hasEmail=false, hasPassword=false, href, title.
  Do NOT type. Do NOT click the checkbox. Mark that part FAIL-engine and continue to the next part that is still allowlisted.
  Admin parts (P1, P2) are expected to FAIL-engine on this Fly path.

---

PART P0 — identity surfaces (Phantom)
Allow hosts: accounts.shopify.com, partners.shopify.com, admin.shopify.com
1. tools/list
2. navigate {"url":"https://accounts.shopify.com/"}
3. wait {"delay_ms":8000}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account]'),hasPassword:!!document.querySelector('input[type=password]'),cf:!!(document.querySelector('[name=cf-turnstile-response],#challenge-form,.cf-turnstile')||/just a moment/i.test(document.title))})"}
5. get_snapshot {"mode":"html"}
6. If cf true: wait {"delay_ms":8000} and evaluate the same expression again.
7. navigate {"url":"https://partners.shopify.com/"}
8. wait {"delay_ms":3000}
9. evaluate same shape. HARD STOP if host is www.shopify.com.
10. If still on partners or accounts: navigate {"url":"https://admin.shopify.com/"}
11. wait {"delay_ms":8000}
12. evaluate same shape.
No type. No click except you may skip click.
Pass P0 only if hasEmail or hasPassword becomes true and cf is false.
Expected on Fly: FAIL-engine, cf true. Not a bounty finding.

---

PART P1 — staff vs owner admin (Phantom)
Allow host: admin.shopify.com
Allow paths prefix: /store/funk-it-up-sdzgxmea
If P0 did not leave you on admin.shopify.com/store/funk-it-up-sdzgxmea with a shop shell:
  write evaluate { "part":"P1","status":"FAIL-engine","reason":"no staff/owner session in Phantom" }
  skip remaining P1 navigates.
Else, one evaluate after each navigate+wait 500:
  /store/funk-it-up-sdzgxmea/products
  /store/funk-it-up-sdzgxmea/products/10323603947706
  /store/funk-it-up-sdzgxmea/settings/general
  /store/funk-it-up-sdzgxmea/settings/payments
  /store/funk-it-up-sdzgxmea/themes
  /store/funk-it-up-sdzgxmea/orders
  /store/funk-it-up-sdzgxmea/customers
EVAL:
JSON.stringify({path:location.pathname,host:location.hostname,title:document.title,denied:/permission|non hai|don't have|access denied/i.test(document.body.innerText),listVisible:!!document.querySelector('[href*="/products/"]'),saveEnabled:!!document.querySelector('button[name*=save],button[aria-label*=Save],button[aria-label*=Salva]')})
Do not click Save. Do not type.
Pass P1 only if host stays admin.shopify.com and each path is recorded.

---

PART P2 — IDOR A ids on store B (Phantom)
Allow host: admin.shopify.com
Allow paths: /store/funk-it-up-sdzgxmea /store/xxxxxx-r48zg9i1
If not authenticated in Phantom: FAIL-engine same as P1, skip.
Else navigate+wait 500+evaluate:
  https://admin.shopify.com/store/xxxxxx-r48zg9i1
  https://admin.shopify.com/store/xxxxxx-r48zg9i1/products
  https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/10323603947706
EVAL add: productA:/10323603947706|hidden snowboard|funk it up/i.test(document.body.innerText)&&location.pathname.includes('xxxxxx-r48zg9i1')
idor true only if productA true on a B path.
Owner-capable session seeing both shops is NOT idor.

---

PART P3 — storefront primitives (Phantom — this part should run)
Allow host: funk-it-up-sdzgxmea.myshopify.com
Allow paths: / /password /products/*
Do not open admin. Do not checkout. Do not type Bogus 1/2/3.
Do not type storefront password unless the user put it in this same turn (they did not).
1. tools/list if this is a new session; else continue the same session only if the previous part HARD_STOP’d cleanly. Prefer a fresh session for P3 if P0/P1 polluted the tab.
2. For each URL, navigate, wait 500, evaluate:
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/the-compare-at-price-snowboard
   https://funk-it-up-sdzgxmea.myshopify.com/products/selling-plans-ski-wax
   https://funk-it-up-sdzgxmea.myshopify.com/products/gift-card
EVAL:
JSON.stringify({title:document.title,path:location.pathname,host:location.hostname,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),availability:(document.body.innerText.match(/sold out|out of stock|hidden|unavailable|archived/i)||[])[0]||null,price:(document.querySelector('[class*=price]')||{}).textContent||null})
If hasPasswordForm and path /password: record gate, skip remaining PDPs. Do not invent the password.
No finding: all OutOfStock on published test SKUs.

---

ORDER: P0 → if FAIL-engine continue P3 in the same or a new SSE session. Do not block P3 on P0.
P1 and P2 only if P0 produced cf=false and an admin shell.
Reply after the battery: one matrix per part, evaluate JSON, final hrefs, archive paths. Stop.
