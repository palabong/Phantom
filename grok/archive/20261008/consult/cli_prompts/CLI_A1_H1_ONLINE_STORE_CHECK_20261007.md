UPDATED: 2026-10-07T17:32Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — online store publication check

Read only. No editor. Password not in this file.

```
Read only. CLI already logged in as palabong@wearehackerone.com on funk-it-up-sdzgxmea.myshopify.com. Do not mutate. Do not open an editor. If an editor opens, exit without saving. Do not touch Phantom.

Check whether the latest inventory and publication changes are on the Online Store channel, not only the world catalog. Handles: the-hidden-snowboard, the-archived-snowboard.

1. shopify store execute --store funk-it-up-sdzgxmea.myshopify.com --query 'query { publications(first: 20) { nodes { id autoPublish catalog { id title } } } }'
2. shopify store execute --store funk-it-up-sdzgxmea.myshopify.com --query 'query { products(first: 2, query: "handle:the-hidden-snowboard OR handle:the-archived-snowboard") { nodes { handle status publishedAt resourcePublications(first: 15) { nodes { isPublished publication { id catalog { title } } } } variants(first: 1) { nodes { id inventoryPolicy sellableOnlineQuantity inventoryQuantity } } } } }'

Reply: Online Store publication id, isPublished on Online Store, isPublished on world, sellableOnlineQuantity, inventoryPolicy, publishedAt. Stop.
```
