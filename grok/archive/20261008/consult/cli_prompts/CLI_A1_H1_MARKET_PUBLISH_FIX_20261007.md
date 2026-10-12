UPDATED: 2026-10-07T17:44Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — market catalog publish

world is a market, not a catalog. Do not select a catalog because its title is world.

```
Owned store fix. CLI already logged in as palabong@wearehackerone.com on funk-it-up-sdzgxmea.myshopify.com. Do not open an editor. If an editor opens, exit without saving and pass --query on the command line. One mutation per command. Do not change status, price, or theme. Do not unpublish Online Store. Do not contact Shopify Support. Do not touch Phantom.

world is a market, not a catalog. Do not pick a catalog by the title world.

1. If a mutation is denied, re-auth read_products,write_products,read_publications,write_publications,read_markets. Stop if auth fails.
2. Read markets with status and the catalogs assigned to each market, plus the publication id of each of those catalogs. Print market name, market status, catalog id, catalog title, publication id.
3. publishablePublish every product onto each publication id from step 2. Do not publish to channel catalogs. Print userErrors.
4. productVariantsBulkUpdate inventoryPolicy CONTINUE on the-hidden-snowboard and the-archived-snowboard only. Print userErrors.
5. Re-read those two handles: status, sellableOnlineQuantity, inventoryPolicy, and isPublished on each market publication from step 2.

Reply: market rows, userErrors, the two handles after. Stop.
```
