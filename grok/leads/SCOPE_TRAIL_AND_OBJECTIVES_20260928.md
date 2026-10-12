UPDATED: 2026-09-28T14:35Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-25T19:22Z
PROJECT: phantom_cloud

# Scope trail validation + unlocked objectives

Source document: attached / `grok/HackerOne Program Selection.md` (dated analysis, not live policy).
Live checks: 2026-09-28 against public HackerOne / vendor bounty pages.
L5 RoE remains binding: allowlist, no credential stuffing, no destructive actions, no off-mandate targets.
Engine freeze stands. This file does not name a production-tree edit.

## 1. Verdict on the attached trail

The document is usable as a **lead list**, not as an engagement plan.

What holds:
- Shopify ceiling $200,000 is current (Shopify rewards page updated 2026-09-27; H1 still lists Critical $50k–$200k).
- Slack RCE Critical $17,000 matrix is current (policy summary updated 2026-08-07).
- Uber Critical $11k–$15k is current.
- Whatnot Critical $10,000 + Gold Standard Safe Harbor is current.
- Agoda Public Critical $5k–$6k + required `User-Agent: hackerone-<handle>` is current. Automation/scanning is explicitly prohibited.
- Box Critical $5,000 and Box AI in-scope *with demonstrated security impact* is current (`box_private`).
- Wolt adopted Gold Standard Safe Harbor. Program is young (launched Jul 2026).
- German EUDI handle `common_codes` is the correct H1 team (d-you / Common Codes GmbH). The attached bibliography was not a broken link.

What does not hold, or must be downgraded:

| Claim in the attached doc | Live assessment |
|---------------------------|-----------------|
| Phantom is an “attack” / WAF-evasion exploit platform | L5: invitational / authorized research only. Stealth is a navigation property, not a license to ignore program automation bans. |
| Engine is “headless Chrome” | L2-arch / L0: `headless=False` on Xvfb is intentional. |
| Vercel Sandbox is a standing $50k web target for AOM/DOM work | Sandbox bounty is **isolation / Firecracker / cross-tenant**, not browser-tooling. Public challenge window was 2026-08-18 → 2026-09-01 (pool $1M, max $50k/report). Status flickered archived↔public in early September. Verify live before any time investment. |
| Anthropic paid ceiling $10,000 as a single public web program | Split surface: `anthropic-vdp` (GSSH, not a paid product bounty), model-safety bounty (invite / classifier jailbreaks; vendor pages cite up to $15k–$35k), product-security track reported separately. Do not treat $10k web XSS as the program. |
| EUDI max $15,000 | Third-party index lists up to $40,000; scope is **Android / TestFlight / sandbox APIs**, not a first-class web app for `get_snapshot`. Recheck the live table before quoting a ceiling. |
| Agoda requires editing `phantom_cloud.py` `init_browser()` | Violates production freeze. HTTP `User-Agent` is a Chrome launch flag, not an `evaluate` patch of `navigator.userAgent`. Park Agoda until a named-path engine change or an out-of-process Chrome flag is authorized. |
| SwiftShader “masked / solved” | L4 stealth eval PASS with caveats. SwiftShader is **not** claimed solved. |
| Safe Harbor = free hand | GSSH waives conflicting ToS for **good-faith research inside that program’s rules**. It does not override scanner bans, PII stop-rules, or third-party infra. |
| Single Fly session can run a ten-program portfolio in parallel | `MAX_CONCURRENT_SESSIONS = 1`. Trail is sequential, not concurrent. |

## 2. Fit filter (engine + RoE)

Keep a lead only if all four are true:

1. Public web (or authenticated web on a **researcher-owned** tenant).
2. Program allows creating test accounts / stores / workspaces.
3. Interaction stays inside the six tools: `navigate`, `get_snapshot` (html\|ax), `click`, `type`, `evaluate`, `wait`.
4. PII of other users is avoidable. If encountered: stop, do not persist snapshots under `runs/`.

Reject or park if the money sits in microVM escape, mobile wallet crypto, model-weight theft, or requires an engine patch.

## 3. Validated waves

### Wave A — engine-native, open now

| # | Program | Live ceiling (Critical) | Why it fits the six tools | Hard RoE |
|---|---------|-------------------------|---------------------------|----------|
| A1 | Shopify | $90k–$200k on shopify.com calculator; H1 band still $50k–$200k. High band on vendor site now $17k–$85k | Own `*.myshopify.com` + admin/partners. Liquid/DOM, auth/ATO campaign surfaces. | Only stores created with `HANDLE@wearehackerone.com`. Never merchant prod. Contacting Shopify Support about the program is a ban path. |
| A2 | Slack | RCE $17k; cross-org authz $10k | Own workspaces. IDOR / CSRF / filter UI. Structured payout matrix = ROI planning. | No scanners. No other-org credentials. Quip/Nebula often Critical-only. |
| A3 | Whatnot | $10k / $5k / $1k / $300 | `www.whatnot.com` + `*.whatnot.com` web. Live commerce + auctions. GSSH. | Third-party infra on the wildcard is out. Impact-priced, not CVSS-pure. |
| A4 | Wolt | Attached doc $3k; live page shows top paid ~$2.5k and young stats | EU marketplace (user / courier / merchant). Business-logic / IDOR. GSSH. CET overlap. | Recheck live reward table before committing hours. Do not touch partner B2B beyond researcher-owned test paths. |
| A5 | Agoda Public | $5k–$6k | Web booking + cashback URLs added 2026-09-01 | **UA header `hackerone-<handle>` required.** Automated scanning prohibited. Scope is three explicit URLs, not the whole site. Engine-flag gated. |

### Wave B — open as leads, not as first engine hours

| # | Program | Live ceiling | Why it stays a lead | Gate before hours |
|---|---------|--------------|---------------------|-------------------|
| B1 | Vercel (platform / OSS / WAF) | OSS Critical historically ~$10k–$15k; Platform Protection $50k was CVE-specific and later paused | Web/WAF is closer to the engine than Sandbox | Separate Sandbox isolation work from web work. Confirm which Vercel H1 team is accepting submissions today. |
| B2 | Vercel Sandbox | $25k–$50k per report during the Aug–Sep 2026 challenge | High ceiling, poor tool fit (microVM / firewall / OIDC) | Only if the program is live **and** the user wants a non-browser research lane. |
| B3 | Uber | $11k–$15k Critical | Huge web surface, mature triage | Immediate stop if other-user PII appears. No local save of rider/driver data. |
| B4 | Anthropic | VDP unpaid; model-safety invite up to $15k–$35k; product track reported ~$15k | `type` + `get_snapshot` can drive Claude UI loops | Do not conflate jailbreak bounty with web product bounty. Apply / confirm which program is open. |
| B5 | German EUDI (`common_codes`) | Attached $15k; index up to $40k | EU identity, CET, sandbox backends exist | Mobile-first. PID/EAA = GDPR landmine. Web MCP is secondary. |
| B6 | Box (`box_private`) | $5k Critical | Web + Box AI with authz impact | Alias `+dev` / `+test1@wearehackerone.com`, max two dev accounts. Likely invite. Hallucinations alone are out. |

## 4. Unlocked objective diagram

Previous lock (pre-2026-09-28): single shortest path = frozen engine + 14-day commercial pilot.

Current phase: **lead evaluation**. All roads open. Engine remains frozen.

```
                    ┌─────────────────────────────────┐
                    │  phantom_cloud engine (FROZEN)  │
                    │  6 tools · fra · 1 session      │
                    │  evidence: 20260924 6-tool PASS │
                    └─────────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
     ┌────────────────┐     ┌────────────────┐     ┌────────────────────┐
     │ V1 first-party │     │ V2 API / MCP   │     │ V3 managed / pilot │
     │ H1 research    │     │ access sales   │     │ continuous sec     │
     └────────┬───────┘     └────────┬───────┘     └─────────┬──────────┘
              │                      │                       │
     ┌────────┴────────┐             │                       │
     │                 │             │                       │
     ▼                 ▼             ▼                       ▼
 Wave A web        Wave B          Same six-tool          L5 commercial/
 Shopify Slack     verify-first    surface sold as        PILOT + RoE
 Whatnot Wolt      Vercel-iso      MCP to security        14-day / 10k
 Agoda (gated)     EUDI mobile     teams / agents         cap / allowlist
                   Anthropic split
                   Uber PII-stop
                   Box invite
```

No vector is closed. Sequencing is capacity (`concurrency = 1`), not strategy lock.

Recommended **evaluation order** only (can be reordered on the next task):

1. Confirm H1 handle eligibility and create researcher-owned tenants for A1 Shopify + A2 Slack.
2. Read live policy the same day as first `navigate` (policy versions move).
3. Keep V3 pilot pack (`COMMERCIAL_ROLLOUT_20260924.md`) ready for a paying customer; it is not cancelled.
4. Park Agoda until UA-header capability exists without an unauthorized engine edit.
5. Treat B-wave as parallel *paper* recon only until a lead is promoted.

## 5. Scope trail to execute (when a Wave A program is chosen)

1. Copy the program’s in-scope origins into a written allowlist. Nothing else is navigable.
2. Provision only program-legal accounts (`@wearehackerone.com` / documented aliases).
3. Smoke the six-tool sequence on that allowlisted app (same order as `20260924T153949Z`), non-destructive.
4. If the page is `about:blank` or not the intended authenticated UI: hard stop (`runs/gitlab_matrix/HARD_STOP.txt`).
5. Work hypotheses that the engine can witness: DOM XSS, IDOR in researcher tenants, authz in self-owned orgs, business logic in researcher shops.
6. On foreign PII: stop. Do not write snapshots that contain it into `runs/`.
7. Report through H1. Do not invent Safe Harbor coverage the live page does not show.

## 6. Still true after unlock

- Production tree frozen until a path is named in the same turn.
- SwiftShader not solved.
- No live tokens in this file.
- DAC7 / Partita IVA is operator-tax advice in the attached essay, not a Phantom Cloud product fact.
- Select-artifact INGEST REVISION remains `2026-09-25T19:22Z` (no production-tree change).
