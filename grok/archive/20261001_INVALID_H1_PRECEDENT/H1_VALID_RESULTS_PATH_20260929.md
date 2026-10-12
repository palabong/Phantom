UPDATED: 2026-09-29T18:45Z
PROJECT: phantom_cloud
OBJECTIVE: valid Shopify H1 report on owned tenant funk-it-up-sdzgxmea
DO NOT close this trail until a submit-ready draft exists or a named class is exhausted with evidence.

Closed as evidence, not as “done Shopify”:
- Storefront recon (no platform bug)
- Fly accounts Turnstile (engine limit)
- Staff Attivo + Products View only
- UI deny: settings, themes, Save/Delete on PDP 10323603947706

A valid report needs one of:
- Staff session reads/writes Sensitive (Settings / Payments / Themes) or Orders/Customers PII
- UI deny + API/GraphQL 200 on the same resource
- Cross-shop IDOR (second store YOU created)
- Storefront logic that changes price/stock/payment outside Bogus-docs
Not valid: password gate, test theme HTML, Intoli stealth, “deny wall works”

Next classes on THIS shop (order):
H1-5  UI vs API — staff session, denied routes + their XHR
H1-6  Storefront primitives — hidden/archived/compare-at/selling-plans/gift-card (customer, own shop)
H1-7  Second own store — cross-shop IDOR only

Do not raise staff grants. Do not Support. Do not Fly login. Do not dump buyer PII into runs/.
