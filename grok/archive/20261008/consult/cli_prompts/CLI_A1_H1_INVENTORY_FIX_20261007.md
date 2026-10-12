UPDATED: 2026-10-07T16:37Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — owned-store inventory fix

Password not in this file. Does not publish or change product status.

```
Owned store setup only. Shopify CLI is already logged in as palabong@wearehackerone.com and authorized on funk-it-up-sdzgxmea.myshopify.com. Do not open a browser except the CLI re-auth if a mutation returns access denied. Do not contact Shopify Support. Do not deploy. Do not touch Phantom or Inspector.

Do not change product status. Do not publish. Do not unarchive. Do not edit theme, price, or other products.

Handles: the-hidden-snowboard, the-archived-snowboard.
Known variants: 50535758364858, 50535758266554. Re-read them. Do not trust the ids if the query disagrees.

1. shopify store execute --store funk-it-up-sdzgxmea.myshopify.com --query 'query { products(first: 2, query: "handle:the-hidden-snowboard OR handle:the-archived-snowboard") { nodes { handle status variants(first: 1) { nodes { id inventoryPolicy inventoryItem { id tracked inventoryLevels(first: 5) { nodes { location { id name } quantities(names: ["available"]) { name quantity } } } } } } } }'
2. If that query is denied, run shopify store auth --store funk-it-up-sdzgxmea.myshopify.com --scopes read_products,write_products,read_inventory,write_inventory and repeat step 1. Stop if auth fails.
3. For each variant, set available to 10 at the first location from step 1:
   inventorySetQuantities with ignoreCompareQuantity true, name available, reason "correction", and an @idempotent key.
4. productVariantsBulkUpdate inventoryPolicy CONTINUE on those two variants only.
5. Repeat the step 1 query.

Reply: handle, status, location id, available before and after, inventoryPolicy after. Stop.
```
