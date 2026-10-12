PROJECT: phantom_cloud
UPDATED: 2026-09-29T21:59Z
ENVIRONMENT: Official Grok Build 4.7 Medium on the device CLI

CWD device production tree. Local Chrome. Staff profile that is now Attivo.
Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A. Do not type passwords.

Owner confirmed staff row Attivo. Grant still Prodotti Visualizza only.
H1-4b deny on /products is stale. This is the one retest.

Land:
https://admin.shopify.com/store/funk-it-up-sdzgxmea/products

Allowlist:
- https://admin.shopify.com/store/funk-it-up-sdzgxmea
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
- https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/*
Forbid: Support, settings, themes, other shops, PCI, Fly, Save if enabled.

1. Staff profile: open /products.
2. Record title, path, denied, listVisible.
3. If list visible: open one test-data product. Do not create.
4. Record writeControlVisible (Save/Aggiorna/Elimina enabled?). If yes: do not submit. Stop.
5. Do not open /settings or /themes.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

evaluate.json:
{
  "source": "local-chrome",
  "rowStatus": "Attivo",
  "products": {
    "href":"",
    "title":"",
    "denied":true|false,
    "listVisible":true|false,
    "productOpened":true|false,
    "writeControlVisible":true|false,
    "viewOnly":true|false
  }
}

PASS if products fields are recorded on this shop.
Expected: listVisible true, writeControlVisible false, viewOnly true.
Finding-candidate only if writeControlVisible true — record, do not save.

Zip. Reply: path, verdict, evaluate JSON. Stop.
