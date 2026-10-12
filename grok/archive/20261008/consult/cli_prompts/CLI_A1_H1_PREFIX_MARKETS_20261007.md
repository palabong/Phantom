UPDATED: 2026-10-07T16:45Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — pre-fix market and inventory read

No mutations. No write scopes. Password not in this file.

```
Read only. Do not mutate. Do not publish. Do not change status, inventory, price, or markets. Do not contact Shopify Support. Do not touch Phantom or Inspector.

Shopify CLI is already logged in as palabong@wearehackerone.com on funk-it-up-sdzgxmea.myshopify.com. Current grant may be read_products only. If a query is denied, re-auth read scopes only: read_products,read_inventory,read_publications,read_markets. Stop if that auth fails. No write scopes.

Goal: list what blocks purchase of the catalog on every enrolled market. Explain the gap. Do not fix it.

1. shopify store execute --store funk-it-up-sdzgxmea.myshopify.com --query 'query { shop { name currencyCode } markets(first: 20) { nodes { id name handle status } } catalogs(first: 20) { nodes { id title status } } publications(first: 20) { nodes { id autoPublish catalog { id title } } } locations(first: 10) { nodes { id name fulfillsOnlineOrders } } }'
2. shopify store execute --store funk-it-up-sdzgxmea.myshopify.com --query 'query { products(first: 50) { nodes { handle status totalInventory tracksInventory resourcePublications(first: 10) { nodes { isPublished publishDate publication { id } } } variants(first: 5) { nodes { id sku inventoryPolicy inventoryQuantity sellableOnlineQuantity } } } } }'

Reply with three lists only:
- enrolled markets and catalogs, with status
- products that cannot be purchased, and the missing piece: status, publication, market catalog, location, available quantity, or inventoryPolicy DENY
- products that are purchasable on every enrolled market
Stop.
```
