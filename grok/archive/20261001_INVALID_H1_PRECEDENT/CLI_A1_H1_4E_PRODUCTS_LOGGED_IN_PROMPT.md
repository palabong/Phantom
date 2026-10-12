PROJECT: phantom_cloud
UPDATED: 2026-09-29T22:16Z
ENVIRONMENT: Official Grok Build 4.7 Medium on the device CLI

CWD device production tree. Local Chrome. Staff session is already logged in.
Do not use Fly. Do not deploy. Do not edit engine files. Token → N/A.
Do NOT type passwords. Do NOT open accounts.shopify.com.

H1-4d 20260929T220340Z FAIL: the “staff” window was logged out (landed /lookup Accedi).
Owner UI: H1 Staff = Attivo, role “Accesso collaboratore, H1 view only”. That row is fine.

Precondition (human, before the agent clicks anything):
- Open the Chrome profile that already signed in as palabong+staff@wearehackerone.com.
- Address bar must already be https://admin.shopify.com/store/funk-it-up-sdzgxmea… (Home or any shop page).
- If you see Accedi / accounts.shopify.com: sign in yourself, then start this prompt.

Allowlist:
- https://admin.shopify.com/store/funk-it-up-sdzgxmea
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/*
Hard stop if host is accounts.shopify.com or www.shopify.com. That is FAIL logged-out, not a product deny.

1. Read current address bar. If not admin.shopify.com/store/funk-it-up-sdzgxmea → FAIL, stop.
2. Navigate https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
3. If redirected to accounts.shopify.com → FAIL logged-out, stop. No type.
4. Record denied, listVisible. If list visible, open one existing product. Do not Save.
5. Record writeControlVisible / viewOnly.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

evaluate.json:
{
  "source": "local-chrome",
  "loggedInAsStaff": true|false,
  "products": {
    "href":"",
    "host":"",
    "denied":true|false,
    "listVisible":true|false,
    "productOpened":true|false,
    "writeControlVisible":true|false,
    "viewOnly":true|false
  }
}

PASS only if host is admin.shopify.com and products fields are filled.
Expected: listVisible true, writeControlVisible false.
Zip. Reply: path, verdict, evaluate JSON. Stop.
