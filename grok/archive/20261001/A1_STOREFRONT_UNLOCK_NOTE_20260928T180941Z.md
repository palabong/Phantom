UPDATED: 2026-09-28T18:15Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# A1 storefront unlock — read of device archive 20260928T180941Z

Source (device): `runs/prod_postdeploy_20260928T180941Z`
Attachment reviewed this session. Engine freeze stands.
Password not stored in this note. Archive leak-scan this session: no password/token hits.

## Verdict

PASS. Reason: storefront unlocked.
Final href: `https://funk-it-up-sdzgxmea.myshopify.com/`
`hasPasswordForm`: false. Path: `/`. Title: funk it up.
Hard stop: none. Sessions: 1.

## Matrix

| step | status | ms |
|------|--------|----|
| tools/list | PASS | 135.8 |
| navigate | PASS | 5154.3 |
| wait 500 | PASS | 645.1 |
| get_snapshot html (before type) | PASS | 69.4 |
| type e2 password field | PASS | 113.4 |
| get_snapshot html (after type) | PASS | 64.4 |
| click e3 Enter | PASS | 101.1 |
| wait 800 | PASS | 1505.5 |
| evaluate | PASS | 242.5 |

Refs from live html snapshots. Owner link e4 not clicked.
Archived html is the pre-navigation password template (steps 4/6). Post-unlock state is the evaluate JSON only — acceptable for this task.

## Not claimed

- Catalog / checkout / admin walk.
- Replacement of baseline `20260924T153949Z`.
- SwiftShader solved.
