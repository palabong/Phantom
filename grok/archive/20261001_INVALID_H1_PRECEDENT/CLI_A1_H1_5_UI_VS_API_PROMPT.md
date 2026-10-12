PROJECT: phantom_cloud
UPDATED: 2026-09-29T18:45Z
ENVIRONMENT: Official Grok Build 4.7 Medium — staff Chrome already logged in

CWD device production tree. Local Chrome staff (H1 Staff / Products View only).
Do not use Fly. Do not deploy. Do not edit engine. Token → N/A.
Do not type passwords. Do not raise permissions. Do not submit Save.

Goal: find a valid-class mismatch — UI wall but data still returned.
If every denied page is wall + no body: record that. Trail stays open; next is H1-6.

Allowlist host: admin.shopify.com
Allowlist paths on /store/funk-it-up-sdzgxmea only:
- /products (sanity: still logged in)
- /orders
- /customers
- /themes
- /settings/general
- /settings/payments
Hard stop if another shop or Support.

Precondition: staff tab already on admin.shopify.com/store/funk-it-up-sdzgxmea. If Accedi → FAIL stop.

For each URL above except /products:
1. Paste in staff address bar.
2. Record: final href, title, deniedUI true|false.
3. DevTools Network (human or agent if visible): first document + any admin graphql/json for that resource.
   Record status 200|403|404|other. Do not copy response bodies that look like customer names/emails/phones.
   If body is product-only on an /orders URL, say so in one short flag: dataClass=products|orders|customers|themes|settings|empty|unknown.
4. Do not click export, refund, charge, publish, install.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

evaluate.json:
{
  "source": "local-chrome",
  "loggedInAsStaff": true,
  "grant": "Prodotti Visualizza",
  "routes": [
    {"path":"/orders","deniedUI":true,"http":null,"dataClass":""}
  ],
  "mismatch": true|false
}

PASS if all five routes recorded.
mismatch true = finding-candidate (stop, do not pivot). mismatch false = ACL consistent; do not call the trail finished.

Zip. Reply: path, verdict, evaluate JSON. Stop.
