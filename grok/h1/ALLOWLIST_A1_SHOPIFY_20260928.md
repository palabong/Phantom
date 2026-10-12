UPDATED: 2026-09-28T18:48Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# Allowlist del giorno — A1 Shopify — 2026-09-28

Lead locked this session: A1 Shopify.
Source of truth for policy: live H1 `https://hackerone.com/shopify` + vendor `https://www.shopify.com/bugbounty` (vendor page last updated 2026-09-27 18:00 UTC).
Criteria table read 2026-09-28 from `https://www.shopify.com/bugbounty/criteria`.
H1 scope versions last listed change 2026-06-05 (Authentication & ATO asset).
This file is not a production-tree edit. Engine freeze stands.
Store hostname is set. First engine `navigate` still requires an explicit go-ahead this turn (no credentials in this file).

## 1. RoE binding (do not waive)

- Test only stores created by the researcher with `HANDLE@wearehackerone.com`.
- Signup path: `https://partners.shopify.com/signup/bugbounty`.
- Live merchant stores: prohibited. Interaction with shops you did not create: prohibited.
- Do not contact Shopify Support (chat / email / phone) about the program or a report. Ban path.
- Scope questions only: `bugbounty@shopify.com`. Vulnerability discussion only on HackerOne.
- Commercial scanners prohibited (program / SECURITY.md).
- Six tools only: `navigate`, `get_snapshot` (html|ax), `click`, `type`, `evaluate`, `wait`.
- `MAX_CONCURRENT_SESSIONS = 1`. Sequential only.
- Foreign PII: stop. Do not persist snapshots under `runs/`.
- `about:blank` or unexpected UI: hard stop.
- No engine edit for this lead. No `phantom_cloud.py` / Dockerfile / fly.toml / requirements.txt.

## 2. Program catalog (live 2026-09-28) — not the day’s navigate list

In scope (Core): `your-store.myshopify.com`, `admin.shopify.com`, `accounts.shopify.com`, `partners.shopify.com`, `shopify.plus`, `shop.app`, `arrive-server.shopifycloud.com`, `*.pci.shopifyinc.com`, Authentication & ATO.

In scope (Non-core / case-by-case bounty): `*.shopify.com` (includes shopifycompass.com; third-party services need impact on `*.myshopify.com` users), `*.shopify.io`, `*.shopifycloud.com`, `*.shopifykloud.com`, `*.shopifycs.com`, `shopifyinbox.com`, `linkpop.com`, Shopify Mobile Applications, Shopify Developed Apps, Shopify Third Party Store (own shops only), Shopify Third Party Apps (report to developer first; Shopify payout not expected — Informative), `https://github.com/Shopify/*` public non-archived.

Out of scope: `community.shopify.com`, `community.shopify.dev`, `academy.shopify.com`, `livechat.shopify.com`, `cdn.shopify.com`, `*.email.shopify.com`, `investors.shopify.com`, `supplier-portal.shopifycloud.com`, Other.

Rewards (do not invent SLA):
- Vendor calculator 2026-09-28: Critical $90k–$200k; High $17k–$85k.
- H1 band still listed Critical $50k–$200k; High $14k–$50k.
- Vendor homepage ceiling $200,000 current as of 2026-09-27.

## 3. Navigable today (engine)

Filled from researcher dossier 2026-09-28 (no street address / phone stored here).

| Field | Value |
|-------|--------|
| Store name | funk it up |
| H1 handle | palabong |
| Partner / store email | palabong@wearehackerone.com |
| Own store hostname | funk-it-up-sdzgxmea.myshopify.com |
| Plan | Grow — App Development / dev store |
| Storefront password | ACTIVE on plan; session unlocked 20260928T180941Z (cookie/session only — password not stored here) |
| Payments | Bogus Gateway only — no Shopify Payments |
| Custom domain | none |
| Theme | test-data (MAIN) |
| Catalog (claimed) | 17 products / 3 collections / 1 order |
| Apps | none installed |

Allowed origins for this session:

- `https://funk-it-up-sdzgxmea.myshopify.com/`
- `https://funk-it-up-sdzgxmea.myshopify.com/password`
- same-host storefront after unlock: `/collections*`, `/products*`, `/pages*`, `/cart`, `/search`, `/policies*`
- `https://funk-it-up-sdzgxmea.myshopify.com/admin` — not this unlock task
- `https://admin.shopify.com/store/funk-it-up-sdzgxmea` — not this unlock task
- `https://partners.shopify.com/` — not this unlock task
- `https://accounts.shopify.com/` — not this unlock task

This task selected pages:
- `/pages/contact`
- `/pages/data-sharing-opt-out`
- `/pages/about`
- `/pages/faq`
Gate intercepts `/` and `/password` only as recovery, then return to the named page.

Not navigable: any other `*.myshopify.com`, merchant production, PCI/CS, mobile, GitHub, linkpop, inbox, random `*.shopify.com`, Support chat, owner “Log in here”.

## 3b. Dossier vs research tenant

The pasted “lancio” checklist is merchandising, not H1 work.

Keep as-is for research:
- App Development store + storefront password + Bogus Gateway = correct isolation. Do not upgrade to live Payments or transfer to a merchant account for bounty hours.
- Do not contact Shopify Support to remove the password or change plan.
- Policy placeholders / theme name `test-data` / single test order are content quality, not by themselves a vulnerability class.
- Shop + POS channels on an owned dev store remain own-tenant; do not touch other merchants’ POS or Shop buyers.

Hypotheses the six tools can witness on this hostname (after go-ahead): Liquid/DOM on owned theme, authz between storefront password page and `/admin`, checkout/Bogus Gateway logic on own cart, IDOR only inside this shop’s objects.

## 4. First six-tool smoke (only after §3 hostname is set)

Same order as accepted archive `runs/prod_postdeploy_20260924T153949Z`, non-destructive, on the owned store or partners admin of that account.

1. `navigate` allowlisted URL
2. `wait`
3. `get_snapshot` html
4. `get_snapshot` ax — last mode owns refs
5. `evaluate` non-destructive (`document.title` class only)
6. `type` only on researcher-owned inputs
7. `click` only refs from the snapshot mode just taken

Do not click `e*` after an ax snapshot.

## 5. Gate

No production-tree writes.
No live tokens, storefront passwords, or admin passwords in this file.
First proposed smoke URL (storefront gate only, unauthenticated): `https://funk-it-up-sdzgxmea.myshopify.com/`
Admin/partners smoke needs an already-open researcher session on the device CLI — this analysis agent does not hold credentials.
Storefront smoke 20260928T164449Z: PASS (type N/A). Final href `/password`. Hard stop none.
Device archive: `runs/prod_postdeploy_20260928T164449Z`. Note: `grok/A1_STOREFRONT_SMOKE_NOTE_20260928T164449Z.md`.
Baseline 6-tool acceptance remains `20260924T153949Z`.
Unlock 20260928T180941Z: PASS. Final href `/`. hasPasswordForm false. Leak-scan clean.
Note: `grok/A1_STOREFRONT_UNLOCK_NOTE_20260928T180941Z.md`.
Pages 20260928T183729Z: PASS four /pages. Gate recovered once on P1. Note: `grok/A1_PAGES_NOTE_20260928T183729Z.md`.
Collections index 20260928T191354Z: PASS, 0 product hrefs in AOM. Products live on /collections/all (17, out of stock).
Products prompt: `grok/CLI_A1_PRODUCTS_PROMPT.md`. Password not stored here.
