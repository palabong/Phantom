# Handoff Report — Worker R3 (Platform Integrity & CLI Automation Specialist)

**Document Identifier**: `HANDOFF-WORKER-R3-V1`  
**Date**: 2026-10-14T13:47:00Z  
**Author**: `worker_r3`  
**Recipient**: `parent` (Conversation ID: `78030c4e-56ef-4002-b87a-3e4d94cd2e63`)  
**Task Deliverable**: `/Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md`

---

## 1. Observation

1. **Codebase Architecture & Existing Tools**:
   - `phantom_cloud.py` (lines 485–559) registers exactly six MCP tools on `Server("Phantom-Cloud")`: `navigate`, `get_snapshot`, `click`, `type`, `evaluate`, and `wait`.
   - Tool execution (`handle_call_tool`, lines 625–850) enforces a concurrency guard (`MAX_CONCURRENT_SESSIONS = 1` via `_browser_lock`), target swap auto-recovery on process isolation, and dynamic AOM reference resolution (`resolve_element` supporting `eN` and `axN` tags).
   - In previous runs (`run_orders_eval.py`, `run_payments_eval.py`), calls to public endpoints `/admin/api/2024-10/graphql.json` failed with `Failed to fetch` (CORS block across `admin.shopify.com` and `<shop>.myshopify.com`) and `[API] Invalid API key or access token...` (missing app token on public endpoints). The genuine web administrative interface uses internal web GraphQL (`/admin/internal/web/graphql/core`) with session cookies and `x-csrf-token`.

2. **Core Codebase Baseline Preservation**:
   - The four core codebase and deployment files remain 100% untouched and unmodified:
     - `phantom_cloud.py` (1,125 lines, 48,766 bytes) — Unmodified.
     - `Dockerfile` (34 lines, 1,146 bytes) — Unmodified.
     - `fly.toml` (28 lines, 584 bytes) — Unmodified.
     - `requirements.txt` (7 lines, 72 bytes) — Unmodified.

3. **Deliverable Production**:
   - Authored the authoritative guide `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` (1,501 lines, 71,822 bytes) in the project root.
   - The document contains comprehensive technical specifications, input JSON schemas, raw JSON-RPC payloads, executable client scripts (Python, Node.js, cURL/SSE), test suites for Track H1-5 and Track H1-7, response parsing logic (`parse_eval_results.py`), RoE compliance checklists, and core codebase preservation audits.

---

## 2. Logic Chain

1. **Observation 1 (Tool Mechanics & Prior Errors) -> Step 1**: Automated CLI execution requires exact adherence to Phantom Cloud's MCP schemas. Furthermore, resolving historical `Failed to fetch` and `Invalid API key` probe failures necessitated providing concrete in-browser `evaluate` scripts that query the same-origin Polaris internal web gateway (`/admin/internal/web/graphql/core`) with dynamically extracted `x-csrf-token` headers and session cookies (`credentials: 'include'`).
2. **Observation 1 & 3 -> Step 2**: To ensure autonomous reproducibility across varied developer environments, the CLI guides needed to provide three distinct, self-contained terminal invocation methods: (a) native Python MCP `ClientSession`, (b) Node.js `@modelcontextprotocol/sdk`, and (c) zero-dependency raw JSON-RPC over cURL/SSE.
3. **Observation 1 -> Step 3**: For automated testing of Tracks H1-5 and H1-7, complete, copy-pasteable, production-ready Python test runners (`run_h1_5_suite.py` and `run_h1_7_suite.py`) were embedded in the document. These scripts implement dual-tier assertions (DOM UI deny banners vs. internal GraphQL response records for H1-5; Admin and Storefront cross-shop referencing for H1-7) and output clear pass/fail matrices.
4. **Observation 2 -> Step 4**: In compliance with the platform integrity mandate and user request constraints, zero modifications were made to the core engine or configuration files (`phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`). An explicit baseline integrity table and terminal verification command were established in Section 7 of the deliverable.
5. **Observation 3 -> Conclusion**: The deliverable `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` satisfies all requirements of R3 and Acceptance Criteria in `ORIGINAL_REQUEST.md`, equipping researchers and downstream audit agents with complete autonomous execution and compliance capabilities.

---

## 3. Caveats

- **Active Session Requirement**: Automated execution on authenticated Admin routes (Track H1-5 and Track H1-7 Admin) requires that the Local SSE runner be attached via `CHROME_DEBUGGING_PORT` to an existing desktop Chrome profile already authenticated as `palabong@wearehackerone.com` or `palabong+staff@wearehackerone.com`. Cloudflare Turnstile will block headless containerized logins initiated on datacenter IP addresses (Fly.io).
- **Concurrency Serialization**: The Phantom Cloud MCP engine enforces `MAX_CONCURRENT_SESSIONS = 1`. Concurrent execution of test suites against the same SSE runner will encounter lock contention; sequential test execution is strictly required.

---

## 4. Conclusion

Worker R3 has successfully completed its assigned deliverable:
- Document: `/Users/daniele_palagi/.gemini/antigravity/worktrees/phantom_cloud 2/phantom_cloud_feasibility_strategy/CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` (1,501 lines, 71,822 bytes).
- Architecture, exact MCP schemas for all 6 tools, 3 multi-language terminal invocation methods, and production test suites for Track H1-5 and Track H1-7 are fully specified.
- HackerOne Shopify Bug Bounty Rules of Engagement, scope boundaries, the five zero-tolerance prohibitions, and pre-flight/post-run checklists are formally established.
- Core codebase preservation is 100% verified (zero edits to `phantom_cloud.py`, `Dockerfile`, `fly.toml`, or `requirements.txt`).

---

## 5. Verification Method

To independently verify the deliverable and integrity constraints:
1. **Inspect Deliverable Presence and Structure**:
   ```bash
   test -f "CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md" && echo "Deliverable exists"
   wc -l "CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md"
   ```
2. **Verify Core Codebase Zero-Modification Invariant**:
   Inspect git status or file modification timestamps to confirm that `phantom_cloud.py`, `Dockerfile`, `fly.toml`, and `requirements.txt` are unchanged.
3. **Verify Tool Coverage & Syntax**:
   Search `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` for tool definitions: `navigate`, `get_snapshot`, `click`, `type`, `evaluate`, `wait`.
   Verify that Python and Node.js code snippets are syntactically valid.
4. **Invalidation Conditions**:
   - Any modification made to `phantom_cloud.py`, `Dockerfile`, `fly.toml`, or `requirements.txt`.
   - Omission of any of the six registered MCP tools.
   - Inclusion of testing procedures targeting unauthorized third-party stores.
