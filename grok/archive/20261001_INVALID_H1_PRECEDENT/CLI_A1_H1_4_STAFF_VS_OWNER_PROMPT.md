PROJECT: phantom_cloud
UPDATED: 2026-09-29T00:58Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Local Chrome only. Two profiles, serial.
Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A.

H1-3b 20260928T225408Z is closed (pending invite, Products View only).
Task H1-4a: accept that invite in a NEW Chrome profile, then compare /settings and /themes as staff vs owner on this shop only.

Shop: funk-it-up-sdzgxmea
Owner profile = the Chrome already on admin Home.
Staff profile = a new Chrome profile / window. Never reuse the owner tab to accept the invite.

Allowlist (both profiles):
- https://admin.shopify.com/store/funk-it-up-sdzgxmea
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/themes
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/organization-account
- accounts.shopify.com only for the staff invite accept
Forbid: Support, other shops, PCI, Fly, granting new permissions, changing the H1 view only role.

Do not paste invite password or mailbox contents into chat or the archive.

1. Owner profile: stay logged in. Do not accept the invite here.
2. Staff profile: open the invite from the researcher alias mailbox. Accept. Land on this shop only. If CF appears, complete it yourself.
3. Staff profile navigate:
   a. https://admin.shopify.com/store/funk-it-up-sdzgxmea
   b. https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings
   c. https://admin.shopify.com/store/funk-it-up-sdzgxmea/themes
   For each: record title, path, whether the page is a working editor/settings home or a deny/upgrade/empty wall. Do not click save, publish, or payment.
4. Owner profile same three URLs (or confirm already known Home). Record the same fields.
5. Do not escalate. Do not tick extra permissions. Stop after the comparison table.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json} new stamp.

evaluate.json:
{
  "source": "local-chrome",
  "inviteAcceptedThisRun": true|false,
  "staffHome": {"href":"","title":"","denied":true|false},
  "staffSettings": {"href":"","title":"","denied":true|false},
  "staffThemes": {"href":"","title":"","denied":true|false},
  "ownerSettings": {"href":"","title":"","denied":true|false},
  "ownerThemes": {"href":"","title":"","denied":true|false}
}

PASS if staff session is on this shop AND settings+themes recorded for both roles.
A deny wall for staff is PASS (expected). Opening Themes editor as staff with only Products View is a finding candidate — record it, do not exploit further in this run.

6. Zip. Reply: path, verdict, evaluate JSON. Stop.
