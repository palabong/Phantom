# Project: Phantom Cloud Operational Security Strategy & Feasibility Evaluation

## Architecture
- Target Platform: Owned Shopify Test Tenants (`funk-it-up-sdzgxmea` and `xxxxxx-r48zg9i1`) owned by `palabong@wearehackerone.com`.
- Execution Subsystem: Phantom Cloud (Starlette ASGI + `nodriver` CDP + MCP 1.0.0 protocol over SSE on `http://127.0.0.1:8000` or Fly.io).
- Core Codebase Preservation: Strict freeze on `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`.
- Output Deliverables Layout: Standalone markdown strategy, feasibility, execution, and verification specifications in the project root.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Track H1-5 Differential Auth Strategy | Operational model capturing Polaris web session cookies and `x-csrf-token` against internal GraphQL (`/admin/internal/web/graphql/core` / `/admin/api/unstable/graphql.json`) to test field-level ACLs vs UI denial (Orders, Customers, Settings, Payments) | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Track H1-7 Cross-Tenant Isolation Strategy | Cross-shop multi-tenant isolation testing between Store A (`funk-it-up-sdzgxmea`) and Store B (`xxxxxx-r48zg9i1`) across Admin API, GraphQL schemas, and Storefront API contexts | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Track H1-6 Storefront Primitives Closure | Evidence-grounded closure document on storefront pricing, sold-out items, and hidden variants based on server-side cart drop behaviors | M1 | ORIGINAL_REQUEST §R1 |
| 4 | Quantitative Feasibility Matrix | 0.0 to 1.0 scoring framework across Execution Feasibility, Detection Feasibility, Vulnerability Probability, and Bounty Impact & Program Eligibility for Tracks H1-5, H1-6, H1-7 | M2 | ORIGINAL_REQUEST §R2 |
| 5 | Local SSE vs Fly.io Architectural Assessment | Comparative assessment of Local SSE runner (`http://127.0.0.1:8000`) vs Fly.io cloud hosting regarding Cloudflare Turnstile blocks, WebGL/SwiftShader fingerprints, and session persistence | M2 | ORIGINAL_REQUEST §R2 |
| 6 | Autonomous CLI Execution Guides | Step-by-step CLI execution guides specifying exact MCP tool call payloads (`navigate`, `get_snapshot`, `evaluate`, `click`, `type`, `wait`) for autonomous terminal execution | M3 | ORIGINAL_REQUEST §R3 |
| 7 | Policy Guardrails & Compliance Checklist | RoE compliance verification checklist confirming all activities remain within Shopify Bug Bounty rules (self-owned stores only, no 3rd-party, no Support contact, zero buyer PII) | M3 | ORIGINAL_REQUEST §R3 |
| 8 | Core Codebase Integrity Verification | Audit verifying zero modifications to `phantom_cloud.py`, `Dockerfile`, `fly.toml`, and `requirements.txt` | M3 / Audit | ORIGINAL_REQUEST §R3 |
| 9 | E2E Testing & Coverage Verification | Comprehensive 4-tier opaque-box test and verification matrix validating all strategy components against acceptance criteria | M4 | ORIGINAL_REQUEST §Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Strategic Operational Plan | Track H1-5, H1-7, H1-6 closure in `STRATEGIC_OPERATIONAL_PLAN.md` | Survey complete | DONE |
| M2 | Feasibility Metrics & Architecture | 4-metric matrix & Local vs Fly.io assessment in `FEASIBILITY_EVALUATION_METRICS.md` | Survey complete | DONE |
| M3 | Autonomous CLI Guides & Policy Guardrails | MCP tool payloads & Compliance Checklist in `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` | Survey complete | DONE |
| M4 | E2E Test Suite & Test Ready | Requirement-driven 4-tier verification suite in `TEST_INFRA.md` & `TEST_READY.md` | M1, M2, M3 | DONE |
| M5 | Review, Adversarial Challenge & Forensic Audit | Verification across reviewers, challenger, and forensic auditor | M1, M2, M3, M4 | DONE |

## Code Layout
- `.agents/teamwork/`: Orchestrator and agent metadata folders.
- `STRATEGIC_OPERATIONAL_PLAN.md`: Deliverable R1 (Operational security strategy, test matrices, endpoint catalogs, request templates, differential criteria, H1-6 closure).
- `FEASIBILITY_EVALUATION_METRICS.md`: Deliverable R2 (4-metric evaluation framework, quantitative matrix, rationales, Local SSE vs Fly.io architectural assessment).
- `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md`: Deliverable R3 (Autonomous CLI execution guides with exact MCP tool payloads, compliance checklist).
- `TEST_INFRA.md`: E2E test suite infrastructure and 4-tier test case catalog.
- `TEST_READY.md`: E2E test readiness attestation and coverage summary.
- `tests/test_e2e_verification.py`: Automated 105-test verification suite (100% pass, 0 facade tests, 282 AST assertions).
- Core Files (FROZEN - NO MODIFICATIONS):
  - `phantom_cloud.py`
  - `Dockerfile`
  - `fly.toml`
  - `requirements.txt`
