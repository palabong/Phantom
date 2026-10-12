PROJECT: phantom_cloud
UPDATED: 2026-09-29T13:14Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
AGENT: Antigravity CLI (agy). Not Grok CLI. Not a new engine.

CWD: device production tree (Drive phantom_cloud).
Do not restart Fly. Do not deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → [REDACTED]. Never print it. Never write it to runs/, SMOKE.md, protocol.json, evaluate.json, stdout logs, or zip names.

This is a doctrine prompt. No live navigate. No tests. No archive until the user names A1 again in a later turn.

## What went wrong in prod_postdeploy_.zip (do not repeat)

- Folder name missing UTC stamp (`prod_postdeploy_` is invalid).
- Mixed three jobs in one zip (shop gate, example.com, stealth note dated 2026-09-23).
- smoke_test_output.txt contained the raw SSE token and navigated example.com.
- evaluate.json was a quoted string, not an object.
- SMOKE.md was two lines; no verdict/reason/matrix.
- stealth_evaluation.md claimed production-grade stealth. That claim is closed: accounts.shopify.com stayed on Cloudflare after 16s (H1-1b HARD_STOP). Do not revive it.

## Hard rules (same as Grok CLI runs that PASS)

1. One SSE session. Six tools only: navigate, get_snapshot, click, type, evaluate, wait.
2. MAX_CONCURRENT_SESSIONS = 1. Sequential only.
3. Written allowlist before the first navigate. Hard stop on about:blank, foreign host, /admin during storefront work, Support, PCI.
4. A1 storefront host only: funk-it-up-sdzgxmea.myshopify.com
5. Do not start A1 at example.com, intoli, fingerprint.com, accounts.shopify.com, partners, or admin.
6. Do not type storefront or Shopify passwords unless the user supplies them in the same turn for a named unlock. Do not persist them.
7. Do not click owner “Log in here”. Do not submit contact or checkout. Do not type 1/2/3 on Bogus.
8. Last snapshot owns refs. After a new get_snapshot, old e*/ax* are dead.
9. Engine freeze. No stealth patch. No Turnstile solver. No “SwiftShader fixed”.
10. Agent writes for analysis stay out of the production tree except runs/prod_postdeploy_<UTC>/ for that one job.

## Archive contract (when a run is later authorized)

Directory: runs/prod_postdeploy_<UTC>/
UTC stamp = YYYYMMDDTHHMMSSZ. mkdir exist_ok=False.
Files: SMOKE.md, protocol.json, evaluate.json. Add html_snapshot.txt / ax_snapshot.txt only if that run took snapshots.
Redact token, emails, phones, passwords before write.
SMOKE.md must have: Target, Server, Sessions 1, Verdict, Reason, Final href, step table.
protocol.json must have: timestamp, target_url, server_url, sessions, verdict, reason, final_href, results[].
evaluate.json must be a JSON object or a list of objects — never a raw string.
One job per zip. No __MACOSX. No leftover stealth essays. No smoke_test_output.txt.

## A1 when the user says run A1 (later turn — not now)

Default A1 is storefront recon on the owned shop, not admin, not H1-4.
First URL: https://funk-it-up-sdzgxmea.myshopify.com/
Allow: / /password /collections* /products* /pages* /cart
Expect password gate unless the user gives the gate password in that same turn.
Pass if host stays allowlisted and tools/list is 6.
Do not call that a Shopify bounty finding.
Do not log the Inspector URL with query string.

## Already closed (do not redo unless named)

- Storefront pages, collections hydrogen + automated-collection, three PDPs, R3 hydrogen cart empty/sold out.
- Fly identity login (H1-1 / H1-1b) HARD_STOP on Turnstile.
- Local-chrome admin Home PASS. Staff invite pending PASS (Products View only, Sensitive off). H1-4a staff-vs-owner not in this zip.

Reply to the operator: doctrine loaded, no run executed, ready for a named A1 URL. Stop.
