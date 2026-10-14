## 2026-10-14T13:37:38Z
You are worker_r1, a strategy and operational security worker.
Your working directory is:
/Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/.agents/teamwork/worker_r1

Read the authoritative user request at:
/Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/.agents/teamwork/ORIGINAL_REQUEST.md

Read the survey reports for technical context:
- /Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/.agents/teamwork/explorer_survey_1/survey_codebase.md
- /Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/.agents/teamwork/explorer_survey_2/survey_tracks.md
- /Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/.agents/teamwork/explorer_survey_3/survey_governance_mcp.md
- /Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/PROJECT.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Core codebase preservation: ZERO modifications to `phantom_cloud.py`, `Dockerfile`, `fly.toml`, or `requirements.txt`.

Your exclusive deliverable is:
`/Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/STRATEGIC_OPERATIONAL_PLAN.md`

Tasks:
Author a comprehensive, highly technical, evidence-grounded Strategic Operational Plan covering:
1. Track H1-5 (UI vs. API Differential Authorization):
   - Operational model capturing authenticated Polaris internal web session tokens and CSRF headers in the local browser context.
   - Comprehensive explanation resolving prior probe failures (`Failed to fetch` / `Invalid API key`) by detailing Polaris SPA interaction with internal web GraphQL endpoints (`/admin/internal/web/graphql/core` and `/admin/api/unstable/graphql.json`) with `credentials: 'include'` and `x-csrf-token`.
   - Complete differential test matrices across restricted staff roles for Orders, Customers, Settings, Payments, Themes, and App Development.
   - Detailed endpoint catalogs, GraphQL query and mutation templates, and differential criteria (UI Denied vs API 200/Authorized).
   - Deep nested connection analysis (auditing whether child connections of permitted objects leak restricted entity data).
2. Track H1-7 (Cross-Shop Multi-Tenant Isolation / IDOR):
   - Cross-tenant object reference test cases evaluating whether Store A credentials (`funk-it-up-sdzgxmea`) can query or mutate Store B objects (`xxxxxx-r48zg9i1`) across Admin API, GraphQL schemas, and Storefront API contexts.
   - Global ID (`gid://shopify/...`) object catalog, shop context binding, tenant isolation failure modes.
   - Differential matrices for 15+ cross-shop test vectors (Admin product/order/settings access, Storefront cart add, variant query, handle lookup).
3. Track H1-6 (Storefront Primitives Closure):
   - Evidence-grounded exhaustion report and formal closure criteria for storefront pricing, sold-out items, and hidden variants based on confirmed server-side cart drop behaviors.
   - Audit of previous runs (`run_h1_6_store_b.py`, `A1_H1_6_RERUN_6_NOTE_20261007T132221Z.md`, `prod_postdeploy_20261007T192921Z`).
   - Technical analysis of Shopify server-side cart validation, inventory policy enforcement (`deny` vs `continue`), and checkout pipeline price isolation.

Write `STRATEGIC_OPERATIONAL_PLAN.md`, update your `progress.md`, write `handoff.md` in your working directory, and notify parent (conversation ID 78030c4e-56ef-4002-b87a-3e4d94cd2e63) via send_message when complete.
