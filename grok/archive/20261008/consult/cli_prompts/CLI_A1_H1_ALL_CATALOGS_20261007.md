UPDATED: 2026-10-07T17:51Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — all catalogs, missing pairs only

```
CLI already logged in as palabong@wearehackerone.com on funk-it-up-sdzgxmea.myshopify.com. No editor. One mutation per command. Do not change status, price, or theme. Do not touch Phantom.

world is a market. Known market publication: gid://shopify/Publication/223609815226. Apply that fix to every catalog and every product. Skip pairs already published. Skip variants already CONTINUE.

1. Read publications: id, catalog title. Read products: handle, published publication ids, variant id, inventoryPolicy.
2. publishablePublish only missing product/publication pairs. Print userErrors.
3. productVariantsBulkUpdate inventoryPolicy CONTINUE only on variants still DENY. Print userErrors.
4. Re-read counts: products, publications, unpublished pairs, variants still DENY.

Reply: those four counts and userErrors. Stop.
```
