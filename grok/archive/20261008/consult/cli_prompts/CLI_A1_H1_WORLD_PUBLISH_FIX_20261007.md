UPDATED: 2026-10-07T17:36Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — world publish and CONTINUE

No editor. Online Store already isPublished true for 17. Cart still empty on hidden and archived. world flag was false in the last parse.

```
Owned store fix. CLI already logged in as palabong@wearehackerone.com on funk-it-up-sdzgxmea.myshopify.com. Do not open an editor. If an editor opens, exit without saving and pass --query on the command line. One mutation per command. Do not change status, price, or theme. Do not unpublish Online Store. Do not contact Shopify Support. Do not touch Phantom.

Online Store is already published for all 17. Do not republish that channel. The world catalog was not present in resourcePublications. Cart add still returns empty for the-hidden-snowboard and the-archived-snowboard.

1. If a mutation is denied, re-auth read_products,write_products,read_publications,write_publications,read_inventory,write_inventory,read_markets. Stop if auth fails.
2. Read catalogs and publications. Take the publication whose catalog title is world. Print that publication id.
3. publishablePublish every product onto that world publication only. Print userErrors.
4. productVariantsBulkUpdate inventoryPolicy CONTINUE on every variant whose policy is still DENY. Print userErrors.
5. Re-read the-hidden-snowboard and the-archived-snowboard: status, world isPublished, Online Store isPublished, sellableOnlineQuantity, inventoryPolicy.

Reply: world publication id, publish userErrors, policy userErrors, the two handles after. Stop.
```
