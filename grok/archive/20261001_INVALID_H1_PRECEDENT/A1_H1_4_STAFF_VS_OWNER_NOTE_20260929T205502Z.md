UPDATED: 2026-09-29T16:57Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# H1-4a staff vs owner — 20260929T205502Z

Device: `runs/prod_postdeploy_20260929T205502Z`
Source: local-chrome. Sessions: 2. Verdict PASS.
inviteAcceptedThisRun: true. Fly not used. Leak-scan clean.

Staff (H1 view only / Products View): home, /settings, /themes all denied=true. Themes editor not opened.
Owner: home ok; /settings → /settings/general; /themes shell on-shop denied=false.

Expected ACL. Not a Shopify bounty finding.
Sensitive permissions still off. Role not changed.
