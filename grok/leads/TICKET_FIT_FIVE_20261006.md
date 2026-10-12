UPDATED: 2026-10-06T23:48Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# Five ticket-fit bounties — 20261006T2348Z

Source: grok/SCOPE_TRAIL_AND_OBJECTIVES_20260928.md, live-checked 2026-09-28. Not rechecked tonight. Engine freeze stands. One session. RoE: researcher-owned tenants only, no scanners, no other-user PII.

1. Shopify. Own `*.myshopify.com`. H1 slices through 2026-10-01 are not a draft. Highest ceiling, work already started.
2. Slack. Own workspaces. IDOR / CSRF / filter UI. RCE matrix $17k as of 2026-08-07. No other-org credentials.
3. Whatnot. `www.whatnot.com` and `*.whatnot.com` web. GSSH. Third-party infra on the wildcard is out.
4. Wolt. EU marketplace, researcher-owned user/courier/merchant paths. GSSH. Reward table was young on 2026-09-28; recheck before hours.
5. Box (`box_private`). Web authz plus Box AI only with demonstrated impact. Alias accounts, max two. Likely invite. Hallucinations alone are out.

Parked: Agoda (UA header needs an engine flag), Vercel Sandbox (microVM), EUDI (mobile), Anthropic model-safety (not this web track), Uber (PII stop).
