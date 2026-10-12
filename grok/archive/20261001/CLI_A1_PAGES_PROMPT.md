PROJECT: phantom_cloud
UPDATED: 2026-09-28T18:25Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree (Drive phantom_cloud).
Inspector already on https://phantom-cloud-engine.fly.dev
Do not restart. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. One session only.

Task: visit four owned storefront pages. Not admin. Not partners. Not catalog crawl. Not checkout.

Allowlist host: funk-it-up-sdzgxmea.myshopify.com
Allowlist URLs (only these, plus / and /password if the gate intercepts):
- https://funk-it-up-sdzgxmea.myshopify.com/pages/contact
- https://funk-it-up-sdzgxmea.myshopify.com/pages/data-sharing-opt-out
- https://funk-it-up-sdzgxmea.myshopify.com/pages/about
- https://funk-it-up-sdzgxmea.myshopify.com/pages/faq
- https://funk-it-up-sdzgxmea.myshopify.com/
- https://funk-it-up-sdzgxmea.myshopify.com/password

Hard stop if about:blank OR hostname ≠ funk-it-up-sdzgxmea.myshopify.com OR admin.shopify.com / accounts.shopify.com / partners.shopify.com OR path /admin.
Do not click “Log in here” / store owner / Account / Support.
Do not open another *.myshopify.com.
Do not type the gate password into a contact/email form.
Do not persist password, emails, phones, or tokens in SMOKE.md / protocol.json / evaluate.json.

Gate password (owned storefront only, if input[type=password]|name=password is present):
bE-4C5TLf)LVmk^

Pages in order:
P1 /pages/contact
P2 /pages/data-sharing-opt-out
P3 /pages/about
P4 /pages/faq

1. tools/list
2. navigate P1
3. wait {"delay_ms":500}
4. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]')})"}
5. Gate recovery ONLY if hasPasswordForm===true AND path is / or /password:
   a. get_snapshot {"mode":"html"}
   b. type {"ref":"<password INPUT e* from this snapshot>","text":"bE-4C5TLf)LVmk^","clear":true}
   c. get_snapshot {"mode":"html"}
   d. click Enter/submit BUTTON e* from step 5c. Never e4 owner login.
   e. wait {"delay_ms":800}
   f. navigate P1 again
   g. wait {"delay_ms":500}
   If no password INPUT: stop. Do not invent selectors.
6. get_snapshot {"mode":"html"}
7. evaluate same expression as step 4. Confirm path is /pages/contact.
8. Repeat for P2, P3, P4: navigate → wait 500 → get_snapshot html → evaluate. No extra clicks. No type unless the gate returns (then same recovery, once, then resume the current page).
9. After P4 evaluate, stop.

Pass if all four final hrefs stay on the four /pages URLs (gate detours to /password then back are ok).
Hard stop on foreign host or /admin.

Do not click-miss. Do not walk menus. Do not submit contact forms.

Archive on the device tree only:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Concatenate per-page evaluate objects. Redact token and password.
Reply: path, matrix, four evaluate JSON, four final hrefs. Stop.
