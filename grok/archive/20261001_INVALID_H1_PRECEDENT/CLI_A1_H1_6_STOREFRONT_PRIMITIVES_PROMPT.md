PROJECT: phantom_cloud
UPDATED: 2026-09-29T19:57Z
ENVIRONMENT: Official Grok Build 4.7 Medium

CWD device tree. Storefront, not admin. Fly Inspector OK for this class (owned shop).
Do not deploy. Do not edit engine. Token → [REDACTED]. One session.
Do not type storefront password unless gate appears and user supplied it this turn.
Do not checkout. Do not type Bogus 1/2/3. Do not admin.

H1-5 admin UI mismatch on staff grant is exhausted (walls + empty themes chrome).
H1-6: customer-visible primitives on the same shop. Finding only if price/availability/hidden state is wrong vs admin intent.

Host: funk-it-up-sdzgxmea.myshopify.com
Allow: / /password /products/* /collections/* /cart
Forbid: admin, accounts, partners, Support, /checkout click.

Targets (navigate + evaluate each, cap 5):
1. /products/the-hidden-snowboard
2. /products/the-archived-snowboard
3. /products/the-compare-at-price-snowboard
4. /products/selling-plans-ski-wax
5. /products/gift-card

EVAL:
JSON.stringify({title:document.title,path:location.pathname,ready:document.readyState,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),availability:(document.body.innerText.match(/sold out|out of stock|hidden|unavailable|archived/i)||[])[0]||null,price:(document.querySelector('[class*=price]')||{}).textContent||null,compareAt:!!/compare|compare-at|was/i.test(document.body.innerText)})

If gate: recover only with user-supplied password this turn, else record gate and skip remaining.

Do not add to cart unless path is already on a listed PDP and hasAddToCart; prefer evaluate-only this run.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json,html_snapshot.txt}
Pass: five evaluates or gate documented.
Not a finding: sold out / test-data copy. Candidate only if a hidden/archived product is fully purchasable contrary to admin, or compare-at shows a false discount you can cart.

Reply: path, matrix, evaluate JSON. Stop.
