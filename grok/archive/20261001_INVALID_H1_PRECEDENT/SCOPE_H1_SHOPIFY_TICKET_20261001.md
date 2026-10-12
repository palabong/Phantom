UPDATED: 2026-09-30T23:03Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

SESSION SCOPE — Shopify H1 ticket

Target: one in-scope, paid Shopify report on researcher-owned stores
  A: funk-it-up-sdzgxmea
  B: xxxxxx-r48zg9i1 (letseewhassup)
Accounts: palabong@wearehackerone.com (owner) and palabong+staff@… (staff, Products View only, Attivo)

What counts as the ticket
- Staff session reads or writes Settings, Payments, Themes, Orders, or buyer PII without that grant
- UI deny + API/GraphQL 200 on the same resource
- Cross-shop IDOR: store B context shows store A objects (product 10323603947706 or equivalent)
- Storefront price/stock/publish state contradicts admin in a way that changes money

What is already measured (not the ticket)
- Staff Products View only; Save/Delete off on PDP 10323603947706
- Orders, customers, settings/general, settings/payments: permission walls
- Themes: empty Online Store chrome
- A→B URL swap: product A did not render in B; B storefront password-gated
- Catalog test SKUs published + OutOfStock on the storefront
- accounts.shopify.com interstitial and partners marketing page: not a finding

Open slice
- Isolated staff on B only (alias not a member of A), then A URLs
- Any remaining UI/API mismatch on the current staff grant that has not been recorded

Done when: a submit-ready draft exists, or that open slice is evidenced closed.
