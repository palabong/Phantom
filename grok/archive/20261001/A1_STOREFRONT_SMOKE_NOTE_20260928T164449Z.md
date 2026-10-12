UPDATED: 2026-09-28T16:50Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# A1 storefront smoke — read of device archive 20260928T164449Z

Source (device, not copied into the production tree here):
`/Users/daniele_palagi/Desktop/phantom_cloud/runs/prod_postdeploy_20260928T164449Z`
Attachment reviewed this session. Engine freeze stands.
Accepted 6-tool baseline remains `runs/prod_postdeploy_20260924T153949Z`. This run is allowlisted storefront evidence, not a replacement baseline (`type` = N/A).

## Verdict

PASS for the declared storefront task. Hard stop: none.
Final href stay-on-allowlist: `https://funk-it-up-sdzgxmea.myshopify.com/password`
Password gate observed: true. Policy: gate is PASS, not a block.

## Matrix

| step | status | ms | note |
|------|--------|----|------|
| tools/list | PASS | 128.1 | 6 tools |
| navigate | PASS | 23979.5 | own storefront; latency is Shopify/cold, not a fail |
| wait | PASS | 693.5 | 500 ms delay |
| get_snapshot html | PASS | 65.6 | 286 B — password page only |
| get_snapshot ax | PASS | 69.7 | 918 B |
| evaluate | PASS | 63.7 | title funk it up; hasPasswordForm true |
| type | N/A | 0 | password not supplied, not invented |
| click hit | PASS | 660.9 | ax14 BUTTON Enter (last mode = ax) |
| click miss | PASS | 10687.9 | #phantom-missing-target not found |

## RoE checks

- Host/path stayed on allowlisted pair `/` → `/password`.
- Did not follow html `e4` / ax16 “Log in here” (owner login).
- Enter without password left the session on `/password`.
- Token in protocol is already masked. No customer PII in snapshots.
- html shows `e1` authenticity_token + `e2` password + owner login link — expected Shopify password template, not a finding by itself.

## Not claimed

- SwiftShader solved.
- Full six-tool type/click campaign on catalog/checkout.
- Admin / partners session.
- Replacement of the 20260924 acceptance smoke.
