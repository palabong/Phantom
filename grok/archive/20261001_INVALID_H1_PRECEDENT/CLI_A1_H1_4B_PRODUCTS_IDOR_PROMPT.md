PROJECT: phantom_cloud
UPDATED: 2026-09-29T21:01Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build 4.7 Medium on the device CLI

CWD device production tree. Local Chrome. Staff profile only for active clicks.
Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A. Do not paste passwords or mailbox contents.

H1-4a 20260929T205502Z is closed: staff deny on home/settings/themes; owner open.
Role unchanged: H1 view only / Prodotti Visualizza only.

Task H1-4b (one archive, two checks, serial):
A. Products as staff — view-only vs save.
B. Deep-link IDOR — staff pastes owner URLs.

Shop: funk-it-up-sdzgxmea
Staff Chrome = the profile that accepted the invite.
Owner Chrome = do not use for writes. Owner URLs below are paste targets only.

Allowlist:
- https://admin.shopify.com/store/funk-it-up-sdzgxmea
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/*
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/general
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/themes
Forbid: Support, other shops, PCI, Fly, granting permissions, Save/Publish if a write control actually works — record then stop.

A — products
1. In the staff profile open https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
2. Record title, path, denied true|false, whether a product list is visible.
3. Open one existing product (test-data SKU). Do not create a product.
4. Record whether Save / Aggiorna / Delete is enabled. If Save is enabled: do not submit. Set writeControlVisible true and stop A.
5. If Save is disabled or missing: viewOnly true.

B — deep links (staff address bar, one at a time)
6. Paste https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/general
   Record final href, title, denied. Do not change settings.
7. Paste https://admin.shopify.com/store/funk-it-up-sdzgxmea/themes
   Record final href, title, denied. Do not open the theme editor. If the editor chrome appears, set themesEditorOpened true and stop — do not publish.
8. Do not test other shops.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json} new stamp.

evaluate.json:
{
  "source": "local-chrome",
  "role": "H1 view only",
  "products": {"href":"","title":"","denied":true|false,"listVisible":true|false,"writeControlVisible":true|false,"viewOnly":true|false},
  "idorSettingsGeneral": {"href":"","title":"","denied":true|false},
  "idorThemes": {"href":"","title":"","denied":true|false,"themesEditorOpened":true|false}
}

PASS if A and B are recorded on this shop.
Expected: products list visible + viewOnly true; both deep links denied.
Finding-candidate only if writeControlVisible true on products OR themesEditorOpened true. Do not exploit.

Zip. Reply: path, verdict, evaluate JSON. Stop.
