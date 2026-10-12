PROJECT: phantom_cloud
UPDATED: 2026-09-28T17:02Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree (Drive phantom_cloud).
Inspector already on https://phantom-cloud-engine.fly.dev
Do not restart. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. One session only.

Task: unlock owned storefront password gate. Not admin. Not partners. Not a catalog campaign.

Allowlist host: funk-it-up-sdzgxmea.myshopify.com
Allowlist paths: / , /password , then after unlock only same-host storefront (/ , /collections* , /products* , /pages* , /cart , /search , /collections , /policies*).
Hard stop if about:blank OR hostname ≠ funk-it-up-sdzgxmea.myshopify.com OR host is admin.shopify.com / accounts.shopify.com / partners.shopify.com OR path looks like /admin.
Do not click “Log in here” / store owner / Account / Support.
Do not open another *.myshopify.com.
Do not persist the password, emails, phones, or tokens in SMOKE.md / protocol.json / evaluate.json.

1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/"}
3. wait {"delay_ms":500}
4. get_snapshot {"mode":"html"}
5. type — parse the html snapshot. Use the INPUT whose label/name is password (expected e*). {"ref":"<that e*>","text":"tohchi","clear":true}
   If no password INPUT: stop. Do not invent a selector on admin/login.
6. get_snapshot {"mode":"html"}
7. click the BUTTON that submits the password form (label Enter / submit). Use e* from step 6 only. Never click e* from step 4 after a new snapshot. Never click the owner “Log in here” link.
8. wait {"delay_ms":800}
9. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,ready:document.readyState,path:location.pathname,hasPasswordForm:!!document.querySelector('input[type=password], input[name=password]')})"}

Pass if: hostname stays allowlisted AND (hasPasswordForm===false OR path is a storefront path other than /password).
Fail / hard stop if still trapped on /password with no other change and click reported error, or if href left the host.

Do not run click-miss. Do not type again. Do not walk the catalog.

Archive on the device tree only:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Redact token and password if they appear in snapshots.
Reply: path, matrix, evaluate JSON, final href. Stop.
