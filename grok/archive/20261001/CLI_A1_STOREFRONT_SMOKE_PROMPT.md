PROJECT: phantom_cloud
UPDATED: 2026-09-28T15:54Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree (Drive phantom_cloud).
Inspector already on https://phantom-cloud-engine.fly.dev
Do not restart. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. One session only.

Allowlist (this task only):
- https://funk-it-up-sdzgxmea.myshopify.com/
- https://funk-it-up-sdzgxmea.myshopify.com/password
Hard stop if location is about:blank or a host not in that pair.
Do not open admin, partners, accounts, other *.myshopify.com, or Support.
Do not type the storefront password. Do not persist merchant/customer PII.

1. tools/list
2. navigate {"url":"https://funk-it-up-sdzgxmea.myshopify.com/"}
3. wait {"delay_ms":500}
4. get_snapshot {"mode":"html"}
5. get_snapshot {"mode":"ax"}
6. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,ready:document.readyState,hasPasswordForm:!!document.querySelector('form, input[type=password], input[name=password]')})"}
7. type — N/A (no password supplied; do not invent one)
8. click — after the LAST snapshot mode only (ax refs if step 5 ran last). Prefer a visible A|BUTTON on this page. If none, skip hit-click and say N/A.
9. click {"selector":"#phantom-missing-target"}  (controlled not-found = PASS)

Expected: storefront password gate on an App Development store. That is PASS, not a block.

Archive on the device tree only:
runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,ax_snapshot.txt,evaluate.json}

Redact tokens. Reply: path, matrix, evaluate JSON, final href. Stop.
