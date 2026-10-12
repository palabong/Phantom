PROJECT: phantom_cloud
UPDATED: 2026-09-29T20:18Z
ENVIRONMENT: Official Grok Build 4.7 Medium

CWD device tree. Local Chrome. No Fly. No deploy. No engine edits. Token → N/A.
Do not type passwords. Do not change permissions. Do not create orders.

Stores:
- A: https://admin.shopify.com/store/funk-it-up-sdzgxmea
- B: https://admin.shopify.com/store/xxxxxx-r48zg9i1

Same owner login on both stores is NOT an IDOR. Owner may switch shops by design.
This run only uses the STAFF session of A (H1 Staff, Products View only) against B, plus one storefront ID swap.

Allowlist:
- admin.shopify.com/store/funk-it-up-sdzgxmea
- admin.shopify.com/store/xxxxxx-r48zg9i1
- funk-it-up-sdzgxmea.myshopify.com
- xxxxxx-r48zg9i1.myshopify.com (if it exists)
Forbid: Support, other merchants, PCI.

Part 1 — staff A vs store B
1. Staff Chrome (not owner). Confirm you are H1 Staff on shop A (products list of A visible).
2. Paste:
   https://admin.shopify.com/store/xxxxxx-r48zg9i1
   https://admin.shopify.com/store/xxxxxx-r48zg9i1/products
   https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/10323603947706
3. For each: final href, title, whether you see shop B admin, shop A data, deny, or 404.
   Finding-candidate only if staff-A sees shop B resources OR sees shop A product 10323603947706 rendered inside shop B.

Part 2 — storefront ID swap (optional if Part 1 is deny/404)
4. Logged-out or customer window:
   https://xxxxxx-r48zg9i1.myshopify.com/products/the-hidden-snowboard
   https://xxxxxx-r48zg9i1.myshopify.com/products/10323603947706
   Record 404 vs A’s product page.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

evaluate.json:
{
  "staffA_on_B_home": {"href":"","saw":"deny|shopB|shopA|404|login"},
  "staffA_on_B_products": {"href":"","saw":""},
  "staffA_on_B_productA_id": {"href":"","saw":""},
  "storefront_B_hidden": {"href":"","saw":""},
  "idor": true|false
}

idor true only if A’s product/order/theme data appears in B’s store context.
Owner switching A↔B does not count.

Zip. Reply: path, verdict, evaluate JSON. Stop.
