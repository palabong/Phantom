UPDATED: 2026-09-28T19:17Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# A1 collections index — 20260928T191354Z

Device: `runs/prod_postdeploy_20260928T191354Z`
Verdict PASS. visited=2 collections=0 products=0.
Leak-scan: clean. Gate: already unlocked (hasPasswordForm false).

Visited:
- /collections — title Collections; links named Hydrogen, Automated Collection; no /products/ paths in AOM
- /collections/all — title Products; “17 products”, all out of stock; product cards as A ids `CardLink-template-…-{productId}` without href text in the AOM

Implication: product handles are in the DOM hrefs, not in the distilled AOM labels. Next run must collect `a[href*="/products/"]` via evaluate, then navigate those URLs. Do not wait on collection activation.
