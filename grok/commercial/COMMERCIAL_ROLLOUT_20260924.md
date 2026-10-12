UPDATED: 2026-09-26T21:42Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-25T19:22Z
PROJECT: phantom_cloud

# Commercial rollout against 20260924 six-tool acceptance

Source of truth for this pack: L5 `commercial/*` (read-only) + L3 `reports/SMOKE.md` + archive `runs/prod_postdeploy_20260924T153949Z`.
This file is an operator pack under `grok/`. It does not edit the production tree.

## 1. Why this sequence is the gate

The frozen engine is sold as the six-tool MCP surface already proven on production:

| Step | Tool | 20260924 result | Binding use in the pilot |
|------|------|-----------------|--------------------------|
| 0 | `tools/list` | PASS 140.8 ms — six tools only | Contract surface. No seventh tool. |
| 1 | `navigate` | PASS 4709.8 ms → `https://test-nextjs-two-hazel.vercel.app/` | Allowlisted target load. Counts toward 10k navigate+snapshot cap. |
| 2 | `get_snapshot` `html` | PASS 136.1 ms / 5990 B | Default AOM. Refs `e*`. |
| 3 | `get_snapshot` `ax` | PASS 180.1 ms / 31179 B | Optional AX. Refs `ax*`. Last mode owns refs. |
| 4 | `type` | PASS 402.0 ms on `input[aria-label='Search logs']` text `PHANTOM-TRACE-9901` | Allowlist + non-destructive only. |
| 5 | `evaluate` | PASS 72.9 ms `{"title":"v0 App","typedVal":"PHANTOM-TRACE-9901"}` | Persistence check after type. |
| 6 | `click` | PASS 140.4 ms on `button[aria-label='Reload log records']` | Allowlist + non-destructive only. |
| 7 | `wait` | PASS 608.1 ms / 500 ms delay | Deterministic pause. |
| 8 | `click` miss | PASS 10698.7 ms `#phantom-missing-target` controlled error | Required failure semantics. |

Acceptance criteria in `PILOT_OFFER.md` that this archive already satisfies on the demo fixture:

- Navigate success on that call: yes (single-run evidence, not a 14-day 95% sample).
- Snapshot p50: html 136 ms / ax 180 ms, both ≪ 8.0 s.
- Zero-crash that session: teardown clean.
- Bypass efficacy: not claimed from this fixture. Stealth claim remains `runs/prod_postdeploy_/stealth_evaluation.md` (2026-09-23 PASS with caveats). SwiftShader is not solved.

Do not substitute the Sannysoft CLI path (`CLI_SANNYSOFT_SMOKE_PROMPT.md`, archive `prod_postdeploy_20260925T190747Z`, click-on-ax FAIL) as the commercial go-live gate.

## 2. What the customer buys (and does not)

From `PILOT_OFFER.md` + `PRICING_FRAME.md` + `ROE_AND_SCOPE.md`:

Included: six tools, 14 calendar days from token activation, ≤ 10,000 combined `navigate` + `get_snapshot` calls, concurrency 1, best-effort availability, agreed allowlist.

Excluded / not contractable in the base pilot: multi-tenant isolation, 99.9% SLA, guaranteed named-WAF bypass, custom residential proxy blocks, schedulers, custom scripts, video/stream extract, credential stuffing, destructive actions, off-allowlist navigation.

Prices, minimums, and overage rates stay in the VDP/BB strategic ranges. This pack does not invent numbers.

## 3. Rollout sequence (operator)

Do not issue a live token in chat, tickets, or this file.

1. **Qualify** — invitational / continuous-security mandate only. Customer names owner of each target. Record legal basis.
2. **RoE countersign** — `ROE_AND_SCOPE.md` zero-tolerance list. Hard stop if the page is `about:blank` / not the intended authenticated UI (`runs/gitlab_matrix/HARD_STOP.txt`).
3. **Allowlist freeze** — exact origins before token activation. Demo fixture used in 20260924 is `https://test-nextjs-two-hazel.vercel.app/` (only if still customer-authorized). Customer app URLs replace it after kickoff.
4. **Token** — dedicated `ph_live_` (or Unkey end-user key). One-time secret channel. Never log plaintext.
5. **Wire** — give the production contract, not the checklist typo variants:
   - SSE `GET https://phantom-cloud-engine.fly.dev/sse/?token=<key>` (trailing slash after `/sse/` required)
   - Messages `POST https://phantom-cloud-engine.fly.dev/messages/t/<token>` (token in path; no `?session_id=` in the advertised contract)
6. **Joint gate** — replay the 20260924 order on the agreed allowlisted app (or the demo fixture). Must include both snapshot modes, one non-destructive `type`+`evaluate`, one `click`, `wait`, and the controlled miss.
7. **Go-live mail** — template in `ONBOARDING_CHECKLIST.md` §2, with the wire URLs from step 5 and the six-tool list. Replace Sannysoft as the default smoke if the customer app is already allowlisted.
8. **14-day ops** — one session at a time. Count only `navigate` + `get_snapshot` toward the 10k cap. Sev1 = dedicated channel. Sev2 = support loop named in the checklist (`support@phantom-cloud.io` as written there; do not invent extra SLAs).
9. **Close / convert** — deliver the measured navigate-success %, snapshot p50, crash count, and a qualitative bypass note. Conversion uses `PRICING_FRAME.md` exclusions plus VDP/BB ranges.

## 4. Customer-facing 6-tool kickoff (English; paste into the go-live note)

```text
Pilot gate (same order as production archive 20260924T153949Z):

1. tools/list — expect exactly: navigate, get_snapshot, click, type, evaluate, wait
2. navigate  {"url":"<ALLOWLISTED_URL>"}
3. get_snapshot  {"mode":"html"}
4. get_snapshot  {"mode":"ax"}
5. type  {"selector":"<allowlisted input>", "text":"<non-destructive probe>", "clear":true}
6. evaluate  {"expression":"JSON.stringify({title:document.title, typedVal:<probe getter>})"}
7. click  {"selector":"<allowlisted non-destructive control>"}
8. wait  {"delay_ms":500}
9. click  {"selector":"#phantom-missing-target"}  — expect controlled not-found

Refs from html snapshots are e*. Refs from ax snapshots are ax*.
Only the last get_snapshot mode is valid for ref-based click/type.
Do not navigate off the allowlist. Do not stuff credentials. Do not run destructive actions.
```

On the 20260924 demo fixture the selectors were:

- type: `input[aria-label='Search logs']` / text `PHANTOM-TRACE-9901`
- click: `button[aria-label='Reload log records']`

Those selectors are fixture-specific. Do not copy them onto a customer origin unless the DOM matches.

## 5. Document deltas (require a named-path directive)

Not applied. Production `commercial/` stays frozen until the user names the path.

| File | Drift vs 20260924 / L2 |
|------|-------------------------|
| `ONBOARDING_CHECKLIST.md` | Default smoke is Sannysoft, not the accepted 6-tool app sequence. SSE written as `/sse?token=` (missing trailing slash). Messages shown with `?session_id=` which is not in the README contract. |
| `PILOT_OFFER.md` | Interaction tools in scope — already aligned. Acceptance table is 14-day aggregate; 20260924 is a single-run gate, not the 95% sample. |
| `PRICING_FRAME.md` | No numeric rates here by design. |
| `ROE_AND_SCOPE.md` | No change required for rollout. |

## 6. Stop conditions

- Off-allowlist URL, credential stuffing, destructive / volume-exhaustion use → immediate suspend (`ROE_AND_SCOPE.md`).
- Page is `about:blank` or not the intended authenticated UI → hard stop. Do not improvise.
- Ask for a named-WAF guarantee, 99.9% SLA, or multi-tenant pool → out of pilot; point at exclusions.
- SwiftShader / WebGL residual questions → caveat only; not a solved claim.
