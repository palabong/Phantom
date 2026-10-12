PROJECT: phantom_cloud
UPDATED: 2026-09-29T21:23Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build 4.7 Medium on the device CLI

CWD device production tree. Local Chrome. Staff profile first, owner only if staff cannot open organization-account.
Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A.

H1-4b 20260929T211515Z: staff /products was a deny wall (listVisible false). This run only confirms the live role. Do not change permissions.

Land:
https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/organization-account

Allowlist:
- https://admin.shopify.com/store/funk-it-up-sdzgxmea
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/organization-account
Forbid: Support, other shops, PCI, Fly, ticking extra boxes, accepting new invites.

1. In the SAME staff profile used for H1-4b, open the land URL.
2. If denied (expected possible): record denied=true. Then open the same URL in the owner profile read-only and record the staff row: status (In attesa / Attivo), role name, granted permissions. Do not edit.
3. If staff can see the page: record the same row fields from staff view. Still do not edit.
4. Do not open /products again in this run.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

evaluate.json:
{
  "source": "local-chrome",
  "staffCanOpenOrgAccount": true|false,
  "rowStatus": "In attesa"|"Attivo"|null,
  "role": "<name or null>",
  "granted": [],
  "sensitiveOff": true|false,
  "viewedFrom": "staff"|"owner"
}

PASS if rowStatus and granted are recorded without permission changes.
Expected: Attivo + Prodotti Visualizza only + sensitiveOff true. That would explain 4b only if /products still denies — then the grant does not map to /products (note it, not a ticket).

Zip. Reply: path, verdict, evaluate JSON. Stop.
