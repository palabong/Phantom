PROJECT: phantom_cloud
UPDATED: 2026-09-29T00:16Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Local Chrome only.
Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A.

Previous run FAIL 20260928T221258Z is closed. Do not start at /settings/users.

Task H1-3b: create one limited staff on the owned store.
Land URL (required first navigation):
https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/organization-account

Allowlist:
- https://admin.shopify.com/store/funk-it-up-sdzgxmea
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/organization-account
- same-store /settings/* only if the UI redirects after this land page
Forbid: Support, other shops, PCI, starting at /settings/users, Fly SSE.

Staff:
- Email: researcher alias only (palabong+staff@wearehackerone.com or another handle@wearehackerone.com you own).
- Do not invite a third person. Do not store invite password.
- NOT owner. Sensitive off: no Manage Settings, no Manage payment settings, no Themes.
- Do not accept the invite in this run.

If macOS assistive access is missing: do not fake a PASS. Stop and ask the operator to click Add staff on this land page, then still write the archive from the resulting URL.

1. Open the land URL. Confirm host admin.shopify.com and path starts with /store/funk-it-up-sdzgxmea/settings/organization-account.
2. From that page only, open add-staff / invite. Submit one limited invite.
3. Do not grant Sensitive permissions.
4. Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json} — new stamp, do not overwrite 20260928T221258Z.

evaluate.json:
{
  "source": "local-chrome",
  "href": "<final href query-redacted>",
  "land": "/store/funk-it-up-sdzgxmea/settings/organization-account",
  "staffCreated": true|false,
  "staffEmailRedacted": "<alias or null>",
  "sensitiveOff": true|false,
  "granted": [],
  "inviteAcceptedThisRun": false,
  "assistiveAccess": true|false
}

PASS only if staffCreated true and sensitiveOff true.
FAIL if land page wrong, assistive blocked and form not completed, Support used, or wrong shop.

5. Zip. Reply: path, verdict, evaluate JSON. Stop.
