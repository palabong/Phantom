PROJECT: phantom_cloud
UPDATED: 2026-09-30T23:18Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
ENVIRONMENT: Official Grok Build 4.7 Medium — operator + local Chrome
CWD device production tree.

Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A.

Do NOT type any password into chat or runs/.
Do NOT raise grants above Prodotti Visualizza.
Do NOT remove palabong+staff@ from store A (keep the measured A grant).
Do NOT contact Support.
Do NOT persist mailbox bodies, reset links, or buyer PII.

Stores:
- A: funk-it-up-sdzgxmea — https://admin.shopify.com/store/funk-it-up-sdzgxmea
- B: xxxxxx-r48zg9i1 (letseewhassup) — https://admin.shopify.com/store/xxxxxx-r48zg9i1
Product id under test (belongs to A): 10323603947706

H1-7 20260930T002300Z already did staff-A → B URLs. idor false. B home opened as org/collaborator chrome. That slice is closed.
This run is the inverse and the only open IDOR class: staff who is a member of B only, then A URLs.

Invite alias (B only): palabong+staffb@wearehackerone.com
If that mailbox cannot receive: use another HANDLE+tag@wearehackerone.com that is not a member of A. Record the alias as staffB_alias_redacted=true (do not write the local-part if different and sensitive). Never use the owner inbox as the staff session.

Allowlist:
- admin.shopify.com/store/xxxxxx-r48zg9i1
- admin.shopify.com/store/funk-it-up-sdzgxmea
- accounts.shopify.com (invite accept / staff login only)
- funk-it-up-sdzgxmea.myshopify.com
- xxxxxx-r48zg9i1.myshopify.com
Forbid: Support, other merchants, PCI, Fly, partners marketing, permission edits after invite.

Part 0 — owner, store B (create isolated staff)
1. Owner Chrome. Open
   https://admin.shopify.com/store/xxxxxx-r48zg9i1/settings/organization-account
   If that path 404s, use B Settings → Users and permissions (same store, not A).
2. Invite palabong+staffb@wearehackerone.com.
   Role: copy of H1 view only. Granted: Prodotti Visualizza only.
   Sensitive off: Impostazioni, Negozio online, Ordini, Clienti, Pagamenti = 0.
3. Owner Chrome, store A users page. Confirm the new alias is NOT a member of A.
   If it appears on A, stop. Verdict FAIL-setup. Do not continue Part 1.
4. Human: accept invite in a NEW Chrome profile (not owner, not existing staff-A).
   Land must be store B admin. Row on B must be Attivo.

Part 1 — staff-B session vs store A (the measurement)
Precondition: staff-B profile. B /products list of B visible (or B home with B shop name). A product list must not already be on screen.
5. Paste, one URL at a time, wait for settle:
   https://admin.shopify.com/store/funk-it-up-sdzgxmea
   https://admin.shopify.com/store/funk-it-up-sdzgxmea/products
   https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603947706
   https://admin.shopify.com/store/xxxxxx-r48zg9i1/products/10323603947706
6. For each record: final href, title, shopNameInChrome (A|B|org|none), deniedUI, productA_rendered (true only if title/SKU/media of 10323603947706 is in the page, not just the digits in the URL).
7. Network (document + first admin GraphQL/JSON for that navigation). Status only + dataClass=products|empty|settings|orders|unknown.
   Do not save response bodies with customer PII. Product title of the test SKU is allowed.
8. Org switcher listing store A is NOT idor. idor true only if product/order/theme/PII objects of A render or return 200 with A data while the session is staff-B.

Part 2 — storefront control (only if Part 1 is deny/404)
9. Logged-out window:
   https://xxxxxx-r48zg9i1.myshopify.com/products/10323603947706
   Record 404 vs A product page vs password gate.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}
mkdir exist_ok=False.

evaluate.json:
{
  "source": "local-chrome",
  "staffB_alias_on_A": false,
  "staffB_row_B": "Attivo"|"In attesa"|null,
  "grant": "Prodotti Visualizza",
  "sensitiveOff": true,
  "routes": [
    {"path":"/store/funk-it-up-sdzgxmea","href":"","shop":"","deniedUI":true,"http":null,"productA_rendered":false,"dataClass":""}
  ],
  "idor": false,
  "orgSwitcherShowsA": false
}

idor true = finding-candidate. Stop. Do not pivot. Then this agent writes the H1 draft from evaluate.json.
idor false + all four admin routes recorded = open slice CLOSED. Not a bounty.

PASS if Part 0 isolation is proven and Part 1 four admin routes are recorded.
FAIL-setup if alias is also on A, or staff lands as owner, or row still In attesa.
HARD_STOP if Support or a third shop.

Reply: path, verdict, evaluate JSON. No passwords. Stop.
