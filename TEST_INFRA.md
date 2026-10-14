# TEST_INFRA.md: Comprehensive E2E Testing Infrastructure & Verification Catalog

**Project**: Phantom Cloud Operational Security Strategy & Feasibility Evaluation  
**Author**: `test_writer_e2e` (E2E Testing Architect)  
**Document Version**: 1.0.0  
**Target Environments**:  
- Store A: `funk-it-up-sdzgxmea` (`https://admin.shopify.com/store/funk-it-up-sdzgxmea` / `https://funk-it-up-sdzgxmea.myshopify.com`)  
- Store B: `xxxxxx-r48zg9i1` (`https://admin.shopify.com/store/xxxxxx-r48zg9i1` / `https://xxxxxx-r48zg9i1.myshopify.com`)  
**Research Account**: `palabong@wearehackerone.com` / `palabong+staff@wearehackerone.com`  
**Core Codebase Preservation**: Strict Freeze on `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`.

---

## 1. Test Philosophy & Methodological Framework

### 1.1 Opaque-Box, Requirement-Driven Verification
This verification suite adheres to strict **opaque-box, requirement-driven principles**:
- **Requirement-Driven**: Every test case is derived directly from authoritative contract sources: `ORIGINAL_REQUEST.md`, `PROJECT.md`, HackerOne Shopify Bug Bounty Rules of Engagement, and empirical baseline surveys (`survey_codebase.md`, `survey_tracks.md`, `survey_governance_mcp.md`).
- **Opaque-Box Evaluation**: Tests evaluate externally observable behaviors, contract schemas, payload structures, HTTP status codes, GraphQL responses, and mathematical scoring properties without requiring internal code modifications.
- **Zero Facade Testing**: Completely eliminated all facade or tautological assertions. All tests execute genuine validation logic parsing deliverable markdown contents, validating AST structures, verifying GraphQL schemas, enforcing cryptographic checksums, testing mathematical invariance bounds, and verifying runtime tool signatures.
- **Independence & Isolation**: Every test case is self-contained, idempotent, sets up its own state, and is independent of test execution order.

### 1.2 Core Codebase Preservation & Boundary Enforcement
The core engine files are completely frozen:
- `phantom_cloud.py` (SHA-256: `b75ed50cd45dff5f71388f792a8b38de7f23e6944562249af82160f69f4126df`)
- `Dockerfile` (SHA-256: `3ccfb3725d1addce0c3134471e2ef52897178b13cbdf1ff3e9c2ef26cdccbb08`)
- `fly.toml` (SHA-256: `0227444e4b6416a358dd70ac83604cf94320cc925fff24d9a5558770a16e196d`)
- `requirements.txt` (SHA-256: `1b217ecb50b1049687abc6958186c826e616e17c6ddfcd95861bd4b658cd5067`)

Any architectural or functional improvement must be documented exclusively as a proposal within markdown specifications, never by editing frozen source files.

### 1.3 Expected Output Derivation & Authoritative Sources
For every test case:
1. **Inputs**: Strictly defined input payloads, document files, URLs, HTTP headers, or parameter dictionaries.
2. **Authoritative Source**:
   - `ORIGINAL_REQUEST.md` (§R1, §R2, §R3, §Acceptance Criteria)
   - `PROJECT.md` (§Architecture, §Feature Inventory, §Milestones, §Code Layout)
   - HackerOne Shopify Bug Bounty Rules of Engagement (Scope baseline 2026-06-05)
   - Empirical Survey Reports (`survey_codebase.md`, `survey_tracks.md`, `survey_governance_mcp.md`)
3. **Pass/Fail Semantics**: Deterministic conditions specifying exact return values, status codes, JSON schema matches, and error boundaries.

### 1.4 Adversarial Verification Categories
The test catalog embeds adversarial edge cases across four key vectors:
1. **Encoding & Escaping Integrity**: Special characters, URL path encoding, GraphQL escape sequences, and cross-origin boundaries.
2. **Invalid Input Combinations**: Stale element references, malformed CSRF headers, cross-tenant object parameter pollution, and out-of-bound numerical scores.
3. **Boundary & Resource Stress**: Zero inventory, negative prices, extreme delay timers, single-session concurrency collisions (client-side serialization policy `MAX_CONCURRENT_SESSIONS = 1` vs engine capacity `MAX_CONCURRENT_SESSIONS = 6`), and SwiftShader fingerprint mismatches.
4. **Platform & Policy Safeguards**: Detection of third-party domains, live payment gateway tokens, Shopify Support contact patterns, and buyer PII leakage.

---

## 2. Feature Inventory Mapping

The 9 features from `PROJECT.md` are mapped to target deliverables, verification modules, and authoritative requirements:

| # | Feature Name | Target Deliverable / Module | Milestone | Authoritative Source | Primary Verification Focus |
|---|--------------|-----------------------------|-----------|----------------------|----------------------------|
| **F1** | Track H1-5 Differential Auth Strategy | `STRATEGIC_OPERATIONAL_PLAN.md` | M1 | ORIGINAL_REQUEST §R1 | Polaris session capture, internal GraphQL endpoint specification (`/admin/internal/web/graphql/core`), resolving prior probe failures, restricted staff RBAC matrices across Orders, Customers, Settings, Payments, Themes, App Dev, and nested connections. |
| **F2** | Track H1-7 Cross-Tenant Isolation Strategy | `STRATEGIC_OPERATIONAL_PLAN.md` | M1 | ORIGINAL_REQUEST §R1 | Cross-tenant object reference vectors between Store A (`funk-it-up-sdzgxmea`) and Store B (`xxxxxx-r48zg9i1`), GID architecture, ambient tenant filter (`WHERE shop_id = ...`), 15+ cross-shop test vectors. |
| **F3** | Track H1-6 Storefront Primitives Closure | `STRATEGIC_OPERATIONAL_PLAN.md` | M1 | ORIGINAL_REQUEST §R1 | Evidence-grounded exhaustion report, server-side cart drop behaviors, inventory policies (`deny` vs `continue`), atomic subtotal recalculation, formal closure declaration ($0 non-bountiable). |
| **F4** | Quantitative Feasibility Matrix | `FEASIBILITY_EVALUATION_METRICS.md` | M2 | ORIGINAL_REQUEST §R2 | 4 continuous metrics (EF, DF, VP, BI) on 0.0–1.0 scale, granular rubrics across 5 intervals, scoring tables with rationales, composite prioritization index, HackerOne bounty tier mappings. |
| **F5** | Local SSE vs Fly.io Architectural Assessment | `FEASIBILITY_EVALUATION_METRICS.md` | M2 | ORIGINAL_REQUEST §R2 | Side-by-side comparison across 10+ dimensions, Cloudflare Turnstile root cause (Datacenter ASN vs Residential ISP), WebGL SwiftShader vs native GPU, Chrome debugging port attachment, single-machine scaling. |
| **F6** | Autonomous CLI Execution Guides | `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` | M3 | ORIGINAL_REQUEST §R3 | Exact MCP payloads across all 6 tools (`navigate`, `get_snapshot`, `evaluate`, `click`, `type`, `wait`), automated execution workflows (Python client, Node.js, cURL/SSE), snapshot mode discipline, hydration delays. |
| **F7** | Policy Guardrails & Compliance Checklist | `CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md` | M3 | ORIGINAL_REQUEST §R3 | RoE compliance verification checklist, strictly self-owned stores (`funk-it-up-sdzgxmea`, `xxxxxx-r48zg9i1`), zero 3rd-party testing, zero Support contact, zero buyer PII, Bogus Gateway only. |
| **F8** | Core Codebase Integrity Verification | Audit & System Verification | M3 / Audit | ORIGINAL_REQUEST §R3 | 100% preservation of `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt` via SHA-256 cryptographic verification and AST validation. |
| **F9** | E2E Testing & Coverage Verification | `TEST_INFRA.md` & `TEST_READY.md` | E2E Track | ORIGINAL_REQUEST §Acceptance Criteria | Comprehensive 4-tier verification suite (>= 104 test cases), automated test runner execution, exit code semantics, attestation of test readiness. |

---

## 3. Test Runner Specification & Execution Commands

### 3.1 Test Runner Architecture
The test suite is implemented in Python as a dual-mode test runner:
1. **Direct CLI Script Execution**: `python3 tests/test_e2e_verification.py`
2. **Standard Unittest Integration**: `python3 -m unittest tests/test_e2e_verification.py`

The test runner:
- Parses and validates deliverable markdown files, ASTs, and structural sections directly on disk (zero fallbacks to internal scratchpads).
- Performs mathematical verification of the 0.0–1.0 feasibility metrics, composite formulas, and bounds ($w_{EF}=0.25, w_{DF}=0.20, w_{VP}=0.25, w_{BI}=0.30$, verifying Track H1-5 CFI = $0.6900$).
- Validates the MCP JSON-RPC schemas and payloads against the official MCP tool specifications in `phantom_cloud.py`.
- Enforces cryptographic SHA-256 file preservation on frozen files (`phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`).
- Validates real-world operational walkthrough scenarios across Tiers 1–4 without tautological self-assertions.
- Generates structured JSON reports (`artifacts/test_results_e2e.json`) documenting pass/fail status, execution duration, and assertion traces.

### 3.2 Verification Commands
To execute the complete E2E test verification suite:

```bash
# Primary Execution Command
python3 tests/test_e2e_verification.py

# Standard Unittest Invocation Command
python3 -m unittest tests/test_e2e_verification.py -v
```

### 3.3 Exit Code Semantics
- **Exit Code 0**: 100% of test cases passed. Zero assertions failed. Codebase integrity 100% verified.
- **Exit Code 1**: One or more test cases failed assertion, schema validation, mathematical bounds, or integrity checks. Detailed failure diagnostic logged to stderr and test report.

---

## 4. Comprehensive Test Case Catalog

The test verification suite contains **105 test cases** organized across four tiers:
- **Tier 1**: Feature Coverage (45 test cases: 5 test cases * 9 features)
- **Tier 2**: Boundary & Corner Cases (45 test cases: 5 test cases * 9 features)
- **Tier 3**: Cross-Feature Combinations (10 test cases: pairwise feature interactions)
- **Tier 4**: Real-World Operational Scenarios (5 comprehensive operational walkthroughs)

```
Total Test Cases: 45 + 45 + 10 + 5 = 105 Test Cases (Exceeds >= 104 requirement)
```

---

### Tier 1: Feature Coverage (45 Test Cases)

#### Feature 1: Track H1-5 Differential Auth Strategy (F1-T1-01 to F1-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F1-T1-01** | Primary Functionality | Polaris Session & CSRF Extraction Model | Target: `admin.shopify.com` page context; DOM selectors: `<meta name="csrf-token">`, `window.__INITIAL_DATA__.csrfToken`. | Documented extractable CSRF token string and authenticated `_admin_session` cookie transmission via `credentials: 'include'`. | PASS if extraction routine defines valid selector and cookies are included in request; FAIL otherwise. |
| **F1-T1-02** | Root-Cause Resolution | Prior Probe Failure Resolution (`Failed to fetch` & `Invalid API key`) | Evaluation of prior test scripts (`run_orders_eval.py`, `H1_5_SYNTHESIS.md`). | Explicit technical proof: `Failed to fetch` caused by CORS between `admin.shopify.com` and `<shop>.myshopify.com`; `Invalid API key` caused by calling public API without `X-Shopify-Access-Token`. | PASS if both failure modes are definitively resolved with CORS and token mechanics; FAIL if either is omitted or vague. |
| **F1-T1-03** | Endpoint Specification | Internal Web GraphQL Endpoint Triad Specification | GraphQL routes: `/admin/internal/web/graphql/core`, `/admin/api/unstable/graphql.json`, and public `/admin/api/{version}/graphql.json`. | Clear architectural distinction: internal gateway accepts session cookies + `x-csrf-token` + `X-Shopify-Web-Source: admin-web`, while public endpoint rejects cookies. | PASS if endpoint triad headers, auth methods, and routing are accurately differentiated; FAIL if public endpoint is conflated with internal gateway. |
| **F1-T1-04** | Role Matrix Coverage | Restricted Staff Differential Role Coverage across Core Domains | Role grant: `Prodotti Visualizza` (Products Only) for `palabong+staff@wearehackerone.com`; target domains: Orders, Customers, Settings, Payments, Themes, App Dev. | Complete differential matrix verifying UI Denied state (URL banner) vs API response (`ACCESS_DENIED` / 200) across all 6 domains. | PASS if all 6 domains are cataloged with UI route, GraphQL root field, and differential verdict; FAIL if any domain is missing. |
| **F1-T1-05** | Deep GraphQL Audit | Nested Connection Data Leakage Analysis | Permitted root object: `Product`; queried child connections: `orders`, `purchases`, `draftOrders`, `supplierCosts`. | Explicit audit methodology checking if child connection resolvers inherit parent permissions or enforce granular field-level ACLs. | PASS if nested connection schema and field authorization directives are analyzed with test query templates; FAIL otherwise. |

#### Feature 2: Track H1-7 Cross-Tenant Isolation Strategy (F2-T1-01 to F2-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F2-T1-01** | Architecture Verification | Global ID (GID) Format & Ambient Tenant Scoping | GID string `gid://shopify/Product/10323603521722` evaluated against tenant context `xxxxxx-r48zg9i1`. | Proof that GID lacks `shop_id` and database query relies on ambient tenant binding (`SELECT * FROM products WHERE id = ? AND shop_id = ?`). | PASS if GID syntax and ambient shard partitioning mechanism are documented and verified; FAIL if GID is claimed to contain shop ID. |
| **F2-T1-02** | Admin Cross-Shop Matrix | Admin Cross-Tenant Navigation & Query Vectors | Store A Staff (`palabong@wearehackerone.com`) navigating to Store B Admin routes (`/store/xxxxxx-r48zg9i1/products`, `/orders`, `/settings`). | Observed behavior: HTTP 404, redirect to login, or permission denial banner. Zero cross-shop administrative leakage. | PASS if Admin cross-tenant vectors return access denied or 404; FAIL if IDOR leakage is claimed without rejection evidence. |
| **F2-T1-03** | Storefront Cross-Catalog | Storefront Cross-Tenant Product & Variant Resolution | Store B storefront querying Store A product numeric ID `10323603521722`, handle `the-hidden-snowboard`, and variant `50535758364858`. | Store B returns HTTP 404 Not Found for Store A handles, product IDs, and AJAX endpoints (`/products/*.js`). | PASS if cross-catalog resolution tests specify 404 expected status and catalog isolation; FAIL otherwise. |
| **F2-T1-04** | Cart Cross-Tenant Injection | Storefront Cross-Tenant Cart Add Injection (`cart/add.js`) | Store B cart add POST request with Store A variant ID: `{"items": [{"id": 50535758364858, "quantity": 1}]}`. | Response: HTTP 422 Unprocessable Entity or HTTP 404 ("Cannot find variant"). Variant rejected by tenant inventory partition. | PASS if expected HTTP status is 422/404 with variant not found error assertion; FAIL if cart add succeeds. |
| **F2-T1-05** | Symmetric Multi-Tenant Check | Symmetric Tenant Isolation Verification (Store B -> Store A) | Store A storefront querying Store B variant `67407288565988` (`beanie`) and product numeric ID `15326172709092`. | Symmetric rejection: HTTP 404 Not Found and HTTP 422 Unprocessable Entity on Store A. | PASS if bi-directional symmetry is tested and verified across both Store A -> Store B and Store B -> Store A; FAIL if unidirectional. |

#### Feature 3: Track H1-6 Storefront Primitives Closure (F3-T1-01 to F3-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F3-T1-01** | Empirical Verification | Store A Hidden & Archived Product Cart Drop Audit | Target: "The Hidden Snowboard" (`variant 50535758364858`) and "The Archived Snowboard" (`variant 50535758266554`). | DOM Add to Cart click executes, but navigation to `/cart` reveals empty cart (`$0.00 USD`). Server drops unorderable items. | PASS if historical run observations confirm server-side drop and empty cart subtotal; FAIL if client display is claimed exploitable. |
| **F3-T1-02** | Catalog State Audit | Store B Active Product Baseline Audit (`run_h1_6_store_b.py`) | Target: `beanie` (`variant 67407288565988`) and `black-sunnies` (`variant 67407280242916`). | Admin status verified: `Active`, published to Online Store, 125 and 25 sellable inventory. Cart add HTTP 200 and $300.00 subtotal represent legitimate commerce. | PASS if legitimate active status is distinguished from authorization flaw; FAIL if active product purchase is labeled a vulnerability. |
| **F3-T1-03** | Server-Side Validation | Server-Side Validation Pipeline & Checkout Boundary Analysis | Price injection attempts: `POST /cart/add.js` with manipulated price field (`{"id": ..., "price": 1}`). | Server-side deserializer discards client `price` property; unit price is resolved exclusively from backend database shard. | PASS if server-side price resolution and client price property stripping are documented and verified; FAIL otherwise. |
| **F3-T1-04** | Inventory Policy Enforcement | Inventory Policy Behavior (`deny` vs `continue`) | Variant with `inventory_policy=deny` and 0 stock vs `inventory_policy=continue`. | `deny` variant triggers line item purging or quantity clamping with warning banner; `continue` permits backorder. | PASS if both inventory policies are analyzed with checkout validation checkpoints; FAIL if policies are conflated. |
| **F3-T1-05** | Formal Exhaustion Declaration | Formal Closure Declaration & Deprecation of Track H1-6 | Evaluation of Track H1-6 across pricing, sold-out items, and hidden variants. | Track H1-6 declared **FORMALLY CLOSED** with $0 bounty eligibility; testing effort redirected to H1-5 and H1-7. | PASS if closure declaration is unequivocal, evidence-backed, and explicitly deprecates further runs; FAIL if left open. |

#### Feature 4: Quantitative Feasibility Matrix (F4-T1-01 to F4-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F4-T1-01** | Metric Framework | 4 Continuous Feasibility Dimensions Definition (0.0 to 1.0) | Feasibility definitions for EF, DF, VP, and BI. | All 4 metrics normalized to continuous [0.0, 1.0] range with explicit architectural definitions. | PASS if all 4 dimensions are mathematically defined on [0.0, 1.0]; FAIL if non-standard or missing metrics. |
| **F4-T1-02** | Granular Scoring Rubric | Granular Mathematical Rubric Across 5 Intervals | Intervals: [0.0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0]. | Concrete criteria provided for each interval across all 4 metrics (e.g. 1.0 = Flawless/Deterministic; 0.0 = Impossible/Blocked). | PASS if 5-interval scoring rubric is fully defined across all 4 metrics; FAIL if intervals are undefined. |
| **F4-T1-03** | Quantitative Matrix | Quantitative Feasibility Matrix Table for H1-5, H1-6, H1-7 | Applied score values: H1-5 (EF:0.85, DF:0.80, VP:0.25, BI:0.85); H1-7 (EF:0.90, DF:0.95, VP:0.15, BI:1.00); H1-6 (EF:0.95, DF:0.95, VP:0.05, BI:0.00). | Fully populated numerical table with scores matching empirical survey baselines within +/-0.05 tolerance. | PASS if all scores are present, valid within [0.0, 1.0], and supported by empirical rationale; FAIL if scores missing. |
| **F4-T1-04** | Composite Scoring & Priority | Composite Feasibility Index & Prioritization Formula | Composite formula: weighted average or geometric mean (e.g., $CI = w_1 EF + w_2 DF + w_3 VP + w_4 BI$). | Track H1-7 ranked highest priority due to critical bounty ceiling ($200k), followed by H1-5 (viable High), with H1-6 ranked lowest (closed). | PASS if composite calculation produces consistent priority ranking (H1-7 > H1-5 >> H1-6); FAIL if closed track ranked high. |
| **F4-T1-05** | Bounty Tier Alignment | Mapping to Shopify HackerOne Bounty Tiers | Shopify bounty program reward tiers: Critical ($50k-$200k), High ($14k-$50k), Medium ($3k-$14k), Low ($500-$3k), Ineligible ($0). | H1-7 mapped to Critical ($50k-$200k); H1-5 mapped to High ($14k-$50k); H1-6 mapped to Ineligible ($0). | PASS if bounty mappings match official HackerOne Shopify criteria exactly; FAIL if misclassified. |

#### Feature 5: Local SSE vs Fly.io Architectural Assessment (F5-T1-01 to F5-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F5-T1-01** | Technical Comparison Table | Side-by-Side Architectural Comparison Table (10+ Dimensions) | Comparative vectors: IP reputation, Turnstile bypass, GPU rasterizer, cross-entropy, session persistence, etc. | Comprehensive table contrasting Local SSE runner (`127.0.0.1:8000`) vs Fly.io cloud hosting across >= 10 technical dimensions. | PASS if >= 10 dimensions are analyzed with side-by-side evidence; FAIL if table has <10 dimensions. |
| **F5-T1-02** | WAF & Turnstile Analysis | Cloudflare Turnstile Interception Dynamics & IP ASN Reputation | Egress from Fly.io datacenter ASN (`AS398606`, Frankfurt) vs Residential ISP connection. | Datacenter IP receives elevated threat score triggering mandatory interactive challenge (`Just a moment...` / `Ci siamo quasi...`); Local residential passes. | PASS if ASN reputation and challenge mechanics on `accounts.shopify.com` are forensically explained; FAIL if Turnstile cause is ignored. |
| **F5-T1-03** | WebGL & Cross-Entropy | WebGL SwiftShader Signatures & Cross-Entropy Incoherence | Chrome flags `--use-angle=swiftshader-webgl` with spoofed renderer `ANGLE (NVIDIA RTX 3080 Direct3D11)` on Linux UA. | Anomaly detection: Direct3D11 on Linux platform is an impossible cross-entropy signal; software rasterizer benchmark reveals SwiftShader. | PASS if GPU spoofing mismatch and anti-bot heuristic trigger are thoroughly detailed; FAIL if SwiftShader is claimed solved. |
| **F5-T1-04** | Desktop Profile Attachment | Chrome Debugging Port (`CHROME_DEBUGGING_PORT`) Attachment | Local runner attaching to existing Chrome instance running with remote debugging port enabled. | Local engine attaches to authenticated session, inheriting `_shopify_s` cookies, `cf_clearance` tokens, and hardware entropy. | PASS if attachment mechanics, tab inspection, and CDP script injection workflow are verified; FAIL otherwise. |
| **F5-T1-05** | Machine Affinity Constraint | Fly.io Single-Machine Affinity Constraint (`min_machines_running = 1`) | Multi-machine deployment scenario on Fly.io with in-memory `sse_transports`. | Multiple machines cause session loss (HTTP 400 "No active SSE session") when POST lands on different VM than GET SSE. Single machine required. | PASS if single-machine constraint and in-memory transport limitation are technically documented; FAIL otherwise. |

#### Feature 6: Autonomous CLI Execution Guides (F6-T1-01 to F6-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F6-T1-01** | Tool Schema Verification | 6 Registered Phantom Cloud MCP Tool Schemas Verification | Tool catalog in `phantom_cloud.py`: `navigate`, `get_snapshot`, `click`, `type`, `evaluate`, `wait`. | Exact schema specifications: parameters, types, required fields, and enumerations (e.g. `mode: ["html", "ax"]`). | PASS if all 6 tools are accurately specified with correct parameter schemas; FAIL if tools are missing or invent unapproved tools. |
| **F6-T1-02** | Automated H1-5 Workflow | Autonomous CLI MCP Payload Sequence for Track H1-5 | Step-by-step sequence: `navigate` -> `wait` (4000ms) -> `get_snapshot` (`ax`) -> `evaluate` (CSRF + GraphQL query). | Self-contained, executable MCP payload sequence capturing CSRF and evaluating differential status. | PASS if sequence includes exact JSON payloads and executable JS evaluation snippet; FAIL if incomplete. |
| **F6-T1-03** | Automated H1-7 Workflow | Autonomous CLI MCP Payload Sequence for Track H1-7 | Step-by-step sequence: `navigate` to Store B -> `wait` (3500ms) -> `evaluate` (cross-tenant object probing via DOM & fetch). | Self-contained, executable MCP payload sequence probing Store A GID on Store B with IDOR assertion. | PASS if sequence includes exact JSON payloads and cross-tenant evaluation logic; FAIL if incomplete. |
| **F6-T1-04** | Terminal Client Methods | Multiple Terminal Invocation Implementations | Client implementations: Python `mcp.client.sse.sse_client`, Node.js MCP SDK, raw cURL / SSE streaming. | Functional code examples for at least two invocation mechanisms connecting to `http://127.0.0.1:8000/sse/?token=...`. | PASS if working code snippets are provided for Python and cURL/JSON-RPC; FAIL if only abstract instructions given. |
| **F6-T1-05** | Operational Discipline | Operational Rules: Reference Lifetime, Concurrency, Hydration | Best practices: AOM ref invalidation after snapshot, `MAX_CONCURRENT_SESSIONS = 1`, and Polaris React 3-4s hydration wait. | Explicit instructions prohibiting stale `eN` refs, prohibiting concurrent workers, and mandating hydration delays. | PASS if all three operational constraints are explicitly stated with operational rationale; FAIL if omitted. |

#### Feature 7: Policy Guardrails & Compliance Checklist (F7-T1-01 to F7-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F7-T1-01** | Account Ownership Verification | Tenant Ownership Verification Checklist | Registered test stores: `funk-it-up-sdzgxmea` (Store A) and `xxxxxx-r48zg9i1` (Store B) owned by `palabong@wearehackerone.com`. | Pre-flight check confirms test execution targets ONLY owned test stores and validates owner identity. | PASS if checklist requires store handle and ownership verification; FAIL if third-party domains permitted. |
| **F7-T1-02** | Third-Party Prohibition | Zero Tolerance: Third-Party Merchant Isolation | Domain filter rule against external `.myshopify.com` domains. | Strict prohibition rule: zero navigation, probing, or automated requests against external merchant stores. | PASS if zero-tolerance prohibition is explicitly enforced with domain allowlist; FAIL if third-party testing permitted. |
| **F7-T1-03** | Support Contact Prohibition | Absolute Ban Trigger: Zero Contact with Shopify Support | Communication rule checking contact channels: live chat, tickets, email, phone. | Strict prohibition rule: zero interaction with Shopify Support. All scope questions directed to `bugbounty@shopify.com`. | PASS if prohibition on contacting Shopify Support is explicitly stated as an immediate ban trigger; FAIL if missing. |
| **F7-T1-04** | Buyer PII Scrubbing | Zero Retention of Buyer PII Policy | Snapshot and logging rules under `runs/` and `artifacts/`. | Strict PII scrubbing policy: test data only; immediate testing halt if third-party PII is encountered. | PASS if zero-retention PII policy and data scrubbing guidelines are documented; FAIL if buyer PII retention is tolerated. |
| **F7-T1-05** | Payment Isolation Gate | Payment Safety Rule: Bogus Gateway Only | Gateway configuration check: `bogus` gateway vs live credit cards. | Strict rule: stores must utilize Bogus Gateway only; zero live credit cards or real currency transactions. | PASS if Bogus Gateway restriction is documented as mandatory pre-flight gate; FAIL if live payments allowed. |

#### Feature 8: Core Codebase Integrity Verification (F8-T1-01 to F8-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F8-T1-01** | Hash Check: `phantom_cloud.py` | Cryptographic Checksum Verification for `phantom_cloud.py` | Target file: `phantom_cloud.py`; expected hash: `b75ed50cd45dff5f71388f792a8b38de7f23e6944562249af82160f69f4126df`. | Computed SHA-256 matches expected baseline hash exactly. | PASS if hash matches 100%; FAIL if hash differs (indicating file modification). |
| **F8-T1-02** | Hash Check: `Dockerfile` | Cryptographic Checksum Verification for `Dockerfile` | Target file: `Dockerfile`; expected hash: `3ccfb3725d1addce0c3134471e2ef52897178b13cbdf1ff3e9c2ef26cdccbb08`. | Computed SHA-256 matches expected baseline hash exactly. | PASS if hash matches 100%; FAIL if hash differs. |
| **F8-T1-03** | Hash Check: `fly.toml` | Cryptographic Checksum Verification for `fly.toml` | Target file: `fly.toml`; expected hash: `0227444e4b6416a358dd70ac83604cf94320cc925fff24d9a5558770a16e196d`. | Computed SHA-256 matches expected baseline hash exactly. | PASS if hash matches 100%; FAIL if hash differs. |
| **F8-T1-04** | Hash Check: `requirements.txt` | Cryptographic Checksum Verification for `requirements.txt` | Target file: `requirements.txt`; expected hash: `1b217ecb50b1049687abc6958186c826e616e17c6ddfcd95861bd4b658cd5067`. | Computed SHA-256 matches expected baseline hash exactly. | PASS if hash matches 100%; FAIL if hash differs. |
| **F8-T1-05** | Proposal Discipline | Code Modification Audit: Proposals in Markdown Only | Entire workspace audit of deliverables vs core engine. | Zero changes to core engine; all architectural modifications documented as proposals in markdown reports. | PASS if no core code files modified and proposals reside in markdown; FAIL if core code edited. |

#### Feature 9: E2E Testing & Coverage Verification (F9-T1-01 to F9-T1-05)

| Test ID | Test Category | Description | Test Inputs | Authoritative Expected Output | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F9-T1-01** | Suite Structure | 4-Tier Test Architecture Structure Verification | Test suite specifications in `TEST_INFRA.md` and runner `tests/test_e2e_verification.py`. | Suite implements 4 distinct tiers: Tier 1 (Coverage), Tier 2 (Boundaries), Tier 3 (Combinations), Tier 4 (Scenarios). | PASS if all 4 tiers are formally defined and implemented; FAIL if any tier is missing. |
| **F9-T1-02** | Test Quantity Assertion | Minimum Test Case Count Assertion (>= 104 Test Cases) | Total cataloged and implemented test cases. | Total count equals 105 test cases (exceeding requirement of >= 104). | PASS if total test count >= 104; FAIL if test count < 104. |
| **F9-T1-03** | Automated Runner | Automated Test Runner Execution & Exit Code | Invocation: `python3 tests/test_e2e_verification.py`. | Execution completes cleanly with exit code 0 and structured JSON summary report. | PASS if exit code is 0; FAIL if non-zero exit code or uncaught exception. |
| **F9-T1-04** | Coverage Matrix | Coverage Summary Matrix & Feature Traceability | Mapping of test cases to Features 1 through 9. | Every feature (F1-F9) has >= 5 Tier 1 and >= 5 Tier 2 tests, with Tier 3 and Tier 4 cross-coverage. | PASS if 100% feature coverage is established in matrix; FAIL if any feature has gap. |
| **F9-T1-05** | Readiness Attestation | Test Readiness Attestation Document (`TEST_READY.md`) | Deliverable: `TEST_READY.md`. | Complete attestation document containing runner command, coverage matrix, feature checklist, and sign-off. | PASS if `TEST_READY.md` exists and contains all required sections; FAIL if missing or incomplete. |

---

### Tier 2: Boundary & Corner Cases (45 Test Cases)

#### Feature 1 Boundaries (F1-T2-01 to F1-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F1-T2-01** | Session Expiry | Expired / Revoked Polaris Session Cookie | Request to `/admin/internal/web/graphql/core` with expired `_admin_session` cookie. | Server returns HTTP 401 Unauthorized or redirects to `accounts.shopify.com/login`. | PASS if treated as session expiry rather than differential authorization bypass; FAIL if misdiagnosed. |
| **F1-T2-02** | Malformed CSRF | Malformed / Empty `x-csrf-token` Header | GraphQL POST request with header `x-csrf-token: ""` or missing header. | Server rejects mutation/query with HTTP 403 Forbidden or CSRF validation error. | PASS if CSRF enforcement rejects request deterministically; FAIL if request accepted without CSRF. |
| **F1-T2-03** | Deep Recursion | Circular / Deeply Nested GraphQL Query Stress | Query requesting circular references: `products { collections { products { collections { ... } } } }` (depth > 15). | Shopify GraphQL engine returns query complexity error: `MAX_DEPTH_EXCEEDED` or `QUERY_COST_EXCEEDED`. | PASS if query complexity rejection is captured without server crash; FAIL if unhandled timeout. |
| **F1-T2-04** | Cross-Origin Preflight | Non-Standard Origin Header Injection | Request from origin `https://malicious-attacker.com` to `/admin/internal/web/graphql/core`. | Browser CORS blocks response; server CORS headers omit attacker origin (`Access-Control-Allow-Origin` missing). | PASS if CORS boundary protects internal endpoint; FAIL if wildcard `*` returned with credentials. |
| **F1-T2-05** | Partial Field Denial | Partial Field-Level Authorization Failure (`errors` + `data`) | GraphQL query requesting valid field (`shop.name`) and restricted field (`shop.paymentSettings`). | Response returns partial `data: {"shop": {"name": "Test"}}` accompanied by `errors: [{"message": "Access denied"}]`. | PASS if differential parser evaluates both `data` and `errors` fields accurately; FAIL if parser misses error. |

#### Feature 2 Boundaries (F2-T2-01 to F2-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F2-T2-01** | Integer Overflow | Extreme / Non-Existent Product & Variant IDs | Querying variant ID `9999999999999999999` (64-bit integer boundary) or `-1`. | Server responds with HTTP 404 Not Found or HTTP 422 Unprocessable Entity cleanly. | PASS if handled gracefully without 500 Internal Server Error; FAIL on unhandled server crash. |
| **F2-T2-02** | Malformed GID | Spoofed / Malformed Global ID Syntax | Requesting `gid://shopify/InvalidType/10323603521722` or `gid://shopify/Product/invalid_str`. | GraphQL resolver returns schema validation error: `INVALID_GLOBAL_ID_FORMAT` or null node. | PASS if malformed GID rejected at schema parsing layer; FAIL if unexpected database exception. |
| **F2-T2-03** | Empty Shop Context | Empty / Null Shop Handle in Administrative URL | Requesting `https://admin.shopify.com/store//products` or `https://admin.shopify.com/store/undefined`. | Polaris router redirects to store selector (`admin.shopify.com/store-switcher`) or returns 404. | PASS if client/server redirects safely without disclosing another tenant's store; FAIL on leakage. |
| **F2-T2-04** | Sub-Resource Path Traversal | Directory Traversal in Product Handle / AJAX API | Requesting `/products/..%2f..%2fadmin%2fshop.json` via storefront HTTP request. | Web server normalizes path and returns HTTP 404 Not Found or HTTP 400 Bad Request. | PASS if path traversal is sanitized and blocked at edge; FAIL if administrative file served. |
| **F2-T2-05** | Cross-Tenant Batching | Batch Cart Add with Mixed Multi-Tenant Variant IDs | Payload containing Store A variant `50535758364858` and Store B variant `67407288565988` in single POST. | Server either rejects entire transaction (HTTP 422) or adds only native tenant variant, dropping alien variant. | PASS if alien variant is stripped or rejected with error notice; FAIL if alien variant added. |

#### Feature 3 Boundaries (F3-T2-01 to F3-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F3-T2-01** | Quantity Overflow | Extreme Cart Quantity Parameter Injection | Submitting `quantity: 2147483647` (Max INT32) or `quantity: 1000000` to `/cart/add.js`. | Server clamps quantity to maximum merchant limit or returns HTTP 422 (`"Quantity exceeds limit"`). | PASS if integer overflow is clamped or rejected; FAIL if subtotal overflows or wraps around. |
| **F3-T2-02** | Negative Quantity | Negative / Zero Cart Quantity Injection | Submitting `quantity: -5` or `quantity: 0` to `/cart/add.js`. | Server treats `0` as no-op or returns HTTP 422; negative quantities rejected or converted to item removal. | PASS if negative quantities do not generate credit balances or negative totals; FAIL on negative charge. |
| **F3-T2-03** | Parameter Tampering | JSON Body Parameter Pollution (`price` injection) | Submitting `{"id": 50535758364858, "quantity": 1, "price": 0, "total_price": 0}`. | Server-side parser ignores `price` and derives price exclusively from database shard ($749.95). | PASS if injected price is completely disregarded by backend; FAIL if cart reflects client price. |
| **F3-T2-04** | State Transition Race | In-Flight Variant Archival / Depletion During Cart Session | Variant added when active, then archived in Admin before transitioning from `/cart` to `/checkout`. | Checkout initialization detects invalid variant state and executes server-side cart drop with alert banner. | PASS if stale variant is purged at checkout initialization; FAIL if archived variant purchased. |
| **F3-T2-05** | Currency Mismatch | Multi-Currency Parameter Incoherence Injection | Submitting request with mismatched currency header (`X-Shopify-Currency: JPY` on USD store). | Storefront converts currency via official exchange rates or enforces store base currency ($USD). | PASS if currency conversions are strictly server-controlled without arbitrage; FAIL on currency mismatch. |

#### Feature 4 Boundaries (F4-T2-01 to F4-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F4-T2-01** | Exact Boundary Values | Exact Interval Boundary Scores (`0.0`, `0.2`, `0.4`, `0.6`, `0.8`, `1.0`) | Edge-case input scores matching interval boundaries exactly. | Mathematical rubric assigns deterministic classification (e.g., `0.8` placed in `[0.8, 1.0]` bracket). | PASS if boundary values map deterministically without ambiguous overlapping; FAIL if boundary unhandled. |
| **F4-T2-02** | Out-of-Bounds Values | Out-of-Bounds Score Validation (`-0.1` and `1.05`) | Invalid score inputs: `EF = -0.05` or `VP = 1.2`. | Validator rejects inputs with `ValueError: Score must be between 0.0 and 1.0 inclusive`. | PASS if out-of-bounds scores raise validation error; FAIL if illegal score silently accepted. |
| **F4-T2-03** | Zero Bounty Weighting | Zero Bounty Score Impact on Feasibility Ranking | Closed track with `BI = 0.00` and high execution `EF = 0.95`. | Feasibility index reflects that zero bounty impact precludes high research prioritization. | PASS if closed track is ranked below actionable tracks regardless of execution ease; FAIL if ranked #1. |
| **F4-T2-04** | Floating-Point Precision | Floating-Point Precision & Rounding Consistency | Scores evaluated to 4 decimal places (e.g. `0.8500` vs `0.8500001`). | Numerical comparison maintains `round(val, 2)` consistency and avoids IEEE-754 precision drift. | PASS if tolerance testing passes within `1e-4`; FAIL on rounding error. |
| **F4-T2-05** | Tied Ranking Resolution | Tied Composite Score Disambiguation | Two tracks with identical composite index (e.g. `0.750` vs `0.750`). | Priority tie-breaker defaults to higher Bounty Impact (`BI`), then higher Vulnerability Probability (`VP`). | PASS if deterministic secondary tie-breaking order is enforced; FAIL on random ordering. |

#### Feature 5 Boundaries (F5-T2-01 to F5-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F5-T2-01** | Proxy Probe Timeout | Residential Proxy Pre-Flight Probe Timeout (2.5s) | Unresponsive proxy server injected into `RESIDENTIAL_PROXY_SERVER`. | `httpx.Client` probe times out after 2.5s; engine logs `proxy_fallback_to_direct_connection` and starts Chrome. | PASS if server falls back to direct connection without crash; FAIL if startup hangs indefinitely. |
| **F5-T2-02** | Multi-Session Collision | Concurrent SSE Connection Collision (`MAX_CONCURRENT_SESSIONS = 1`) | Attempting to establish 2 simultaneous SSE streams to `http://127.0.0.1:8000/sse`. | Second connection receives HTTP 429 Too Many Requests or is queued under `_browser_lock`. | PASS if concurrency guard preserves single active session; FAIL if parallel workers corrupt CDP state. |
| **F5-T2-03** | SwiftShader Precision Probe | Deep WebGL Precision & Extension Probing | JavaScript shader micro-benchmark evaluating `highp float` precision and extension list. | SwiftShader software rendering exposed by lack of hardware float precision; logged as cloud engine fingerprint. | PASS if software rasterizer limitations are identified and attributed to cloud container; FAIL if ignored. |
| **F5-T2-04** | Turnstile Hard-Stop Gate | Turnstile Challenge Detection & Hard-Stop Execution | Navigation encounters page title `Just a moment...` or element `iframe[src*='cloudflare']`. | Engine detects challenge, sets `challenge = true`, avoids clicking checkbox, and executes immediate `HARD_STOP`. | PASS if automated clicking is avoided and execution halts safely; FAIL if engine attempts to click CAPTCHA. |
| **F5-T2-05** | Target Swap Process Crash | CDP Process Swap Disconnect During OAuth / Domain Hop | Origin switch from `admin.shopify.com` to `accounts.shopify.com` triggering Chrome process swap. | Target swap auto-recovery invokes `browser.update_targets()`, re-binds `state.page`, and re-injects stealth script. | PASS if CDP session recovers and re-injects stealth payload; FAIL if CDP target disconnects permanently. |

#### Feature 6 Boundaries (F6-T2-01 to F6-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F6-T2-01** | Invalid Tool Call | Unregistered / Malformed MCP Tool Name Invocation | JSON-RPC tool call requesting `"name": "unapproved_custom_scanner"`. | Server responds with JSON-RPC error code `-32601` (`Method not found` / `Unknown tool`). | PASS if unregistered tool rejected with standard JSON-RPC error; FAIL if server crashes. |
| **F6-T2-02** | Missing Parameters | MCP Tool Call Missing Mandatory Schema Parameters | Calling `navigate` with empty arguments `{}` (missing `"url"`). | Tool returns validation error: `"Missing required argument 'url'"`. | PASS if missing required parameter returns clear error message; FAIL on null pointer exception. |
| **F6-T2-03** | Stale Element Reference | Tool Call Using Stale Element Ref (`e1` after new snapshot) | Calling `click ref="e1"` after subsequent `get_snapshot mode="ax"` (which resets to `axN`). | Engine returns element resolution error: `"Element ref 'e1' not found in active element_map"`. | PASS if stale ref rejected gracefully; FAIL if arbitrary element clicked. |
| **F6-T2-04** | Negative Delay Value | Negative or Out-of-Range Delay in `wait` Tool | Tool call: `wait` with `delay_ms: -500` or `timeout_ms: -1000`. | Tool normalizes negative delay to `0` or returns parameter validation error. | PASS if negative delay handled safely; FAIL on infinite sleep or runtime error. |
| **F6-T2-05** | Large Evaluation Buffer | Massive JavaScript Evaluation String Buffer (>1MB) | `evaluate` expression containing 1MB script payload. | Browser handles payload without buffer overflow; returns stringified JSON or truncation notice. | PASS if large script executes or rejects cleanly without crashing CDP connection; FAIL on process kill. |

#### Feature 7 Boundaries (F7-T2-01 to F7-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F7-T2-01** | Third-Party Domain Injection | URL Navigation Attempt to External Merchant Store | Tool call: `navigate url="https://gymshark.com"` or `target-store.myshopify.com`. | Pre-flight guard intercepts URL: `"BLOCKED: Navigation to third-party domain violates RoE"`. | PASS if unauthorized domain blocked by policy guard; FAIL if navigation allowed. |
| **F7-T2-02** | Support URL Detection | Navigation Attempt to Shopify Support Help Center | Tool call: `navigate url="https://help.shopify.com"` or `contact support` link click. | Compliance filter blocks navigation: `"CRITICAL: Contacting Shopify Support triggers immediate ban"`. | PASS if support URLs are intercepted and blocked; FAIL if support portal navigated. |
| **F7-T2-03** | Live Payment Gateway Check | Live Payment Gateway Activation / Mutation Attempt | GraphQL mutation attempting to enable live `shopify_payments` or stripe processing. | Compliance audit rejects mutation: `"BLOCKED: Only Bogus Gateway permitted for test accounts"`. | PASS if live gateway changes blocked; FAIL if real payment processing enabled. |
| **F7-T2-04** | PII Pattern Leakage | Synthetic Buyer PII Regex Detection in Snapshot / Logs | Snapshot contains regex matching live credit cards or unredacted personal phone/address. | PII sanitizer flags record, redacts sensitive string, or halts run: `"HALT: Buyer PII pattern detected"`. | PASS if PII patterns flagged and scrubbed; FAIL if raw buyer PII stored in test runs. |
| **F7-T2-05** | Destructive Action Block | Destructive Shopify Action Attempt (Store Deletion / Transfer) | GraphQL mutation attempting `shopDelete` or plan transfer to production billing. | Safeguard blocks destructive operation: `"BLOCKED: Destructive store mutations strictly prohibited"`. | PASS if destructive operations blocked; FAIL if destructive actions permitted. |

#### Feature 8 Boundaries (F8-T2-01 to F8-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F8-T2-01** | Byte Tampering Detection | Single-Byte Tampering Injection on `phantom_cloud.py` | Simulated modification of a single comment character in `phantom_cloud.py`. | Integrity audit calculates new SHA-256 hash, detects mismatch with baseline, and aborts with error. | PASS if single-byte edit triggers immediate integrity violation; FAIL if modification undetected. |
| **F8-T2-02** | Dockerfile Image Tampering | Dockerfile Base Image Modification Check | Simulated change of base image in `Dockerfile` (e.g. python:3.11 to ubuntu:latest). | Integrity audit detects checksum difference on `Dockerfile` and fails validation. | PASS if Dockerfile changes flagged; FAIL if modified Dockerfile accepted. |
| **F8-T2-03** | Fly Scaling Tampering | `fly.toml` Scaling Configuration Tampering | Simulated change of `min_machines_running` from `1` to `2` in `fly.toml`. | Integrity audit detects checksum difference on `fly.toml` and fails validation. | PASS if `fly.toml` edits flagged; FAIL if modified config accepted. |
| **F8-T2-04** | Dependency Drift | `requirements.txt` Dependency Version Drift | Simulated modification of package versions in `requirements.txt`. | Integrity audit detects checksum difference on `requirements.txt` and fails validation. | PASS if dependency drift flagged; FAIL if version changes tolerated. |
| **F8-T2-05** | Untracked Core Additions | Injection of Untracked Shadow Core Script | Simulated creation of executable script attempting to replace or bypass `phantom_cloud.py`. | Audit flags unauthorized shadow core files outside `.agents/` or `tests/`. | PASS if unauthorized engine scripts flagged; FAIL if shadow cores permitted. |

#### Feature 9 Boundaries (F9-T2-01 to F9-T2-05)

| Test ID | Boundary Vector | Description | Boundary Inputs | Expected Output & Error Handling | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F9-T2-01** | Missing Tier Detection | Incomplete Test Specification Missing an Entire Tier | Ingestion of test specification omitting Tier 2 or Tier 3. | Validation suite raises schema error: `"MISSING_TIER: Suite must contain all 4 tiers"`. | PASS if missing tier is detected and rejected; FAIL if incomplete suite passes. |
| **F9-T2-02** | Test Count Regression | Test Catalog Count Falling Below Mandatory Minimum (<104) | Test catalog containing only 100 test cases. | Validation suite raises assertion error: `"INSUFFICIENT_TESTS: Catalog contains 100 < 104 minimum"`. | PASS if test count < 104 fails assertion; FAIL if count < 104 is accepted. |
| **F9-T2-03** | Corrupted Test Report | Corrupted / Non-JSON Test Output Generation | Test runner outputting non-JSON syntax or unclosed braces. | Report parser raises JSONDecodeError and flags test execution failure. | PASS if corrupted report fails validation; FAIL if malformed output ignored. |
| **F9-T2-04** | Non-Deterministic Flake | Non-Deterministic Assertion Masking Detection | Test using non-deterministic time/PID comparisons without regex tolerance. | Static analysis flags fragile assertions; enforces deterministic regex tolerance. | PASS if non-deterministic assertions flagged; FAIL if flaky tests accepted. |
| **F9-T2-05** | Invalidation Recovery | Invalidation Condition Handling on Sub-Deliverable Updates | Modification of sub-deliverable markdown files during test execution. | Test runner detects file mtime change, invalidates previous test cache, and re-executes verification. | PASS if cache invalidation re-triggers verification; FAIL if stale results returned. |

---

### Tier 3: Cross-Feature Combinations (10 Test Cases)

| Test ID | Feature Pair | Combination Scenario Description | Joint Test Inputs | Expected Inter-Module Interaction | Pass/Fail Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **COMB-T3-01** | F1 (Diff Auth) + F4 (Feasibility) | Feasibility Scoring Grounded in Empirical GraphQL Differential Data | Empirical differential status from H1-5 runs evaluated against VP and DF scoring rubrics. | High DF (0.80) justified by clear `ACCESS_DENIED` vs data return; moderate VP (0.25) justified by core authorization directives. | PASS if feasibility scores directly reflect GraphQL authorization mechanics; FAIL on disconnected scores. |
| **COMB-T3-02** | F1 (Diff Auth) + F6 (CLI Guides) | End-to-End MCP Payload Sequence for Track H1-5 Differential Testing | Step-by-step MCP tool calls (`navigate`, `wait`, `get_snapshot`, `evaluate`) executing differential audit. | Python client script and cURL sequences successfully execute differential query against `/admin/internal/web/graphql/core`. | PASS if payload sequence matches internal GraphQL contract and extracts CSRF; FAIL on schema mismatch. |
| **COMB-T3-03** | F1 (Diff Auth) + F7 (RoE Rules) | Staff Privilege Testing Restricted to Owned Stores Under RoE | Differential testing targeting `funk-it-up-sdzgxmea` with staff account `palabong+staff@wearehackerone.com`. | Verified zero PII collection, zero interaction with third-party merchants, and strict adherence to Bug Bounty scope. | PASS if differential test sequence contains RoE guardrails; FAIL if testing breaches store boundary. |
| **COMB-T3-04** | F2 (Cross-Tenant) + F4 (Feasibility) | Critical Bounty Tier Alignment with Multi-Tenant Architecture | Cross-tenant isolation evaluation mapped to HackerOne bounty tiers ($50k-$200k). | Highest Bounty Impact (`BI = 1.00`) justified because cross-tenant IDOR represents a Critical core bypass; low VP (0.15) justified by ambient shard filters. | PASS if bounty valuation and vulnerability probability reflect tenant architecture; FAIL on misaligned tier. |
| **COMB-T3-05** | F2 (Cross-Tenant) + F6 (CLI Guides) | Autonomous MCP Automation of Cross-Shop GID Probing | MCP tool calls (`navigate`, `wait`, `evaluate`) executing 15-vector cross-shop matrix. | Tool sequence probes Store A GIDs within Store B context and correctly asserts HTTP 404 / 422 rejections. | PASS if cross-shop matrix automated via MCP payloads without manual intervention; FAIL if incomplete. |
| **COMB-T3-06** | F2 (Cross-Tenant) + F7 (RoE Rules) | Multi-Tenant Testing Strictly Confined to Store A and Store B | Cross-tenant matrix inputs referencing exclusively `funk-it-up-sdzgxmea` and `xxxxxx-r48zg9i1`. | Pre-flight assertion confirms both tenant handles belong to `palabong@wearehackerone.com`; zero third-party handles probed. | PASS if cross-tenant matrix strictly restricted to researcher's owned tenants; FAIL on external handle. |
| **COMB-T3-07** | F3 (Closure) + F4 (Feasibility) | Closed Class Feasibility Score Alignment with Cart Drop Observations | Track H1-6 scoring (`VP = 0.05`, `BI = 0.00`, overall `0.49`) mapped to server-side cart drop proof. | Ineligible bounty status ($0) mathematically confirmed; closed status reflected in prioritization index. | PASS if H1-6 scores mathematically enforce its closed status; FAIL if closed track receives bounty weight. |
| **COMB-T3-08** | F5 (Local vs Fly) + F6 (CLI Guides) | Execution Engine Routing for Authenticated MCP Workflows | Routing rule: Local SSE runner (`127.0.0.1:8000`) for authenticated admin; Fly.io for public probes. | MCP guide directs researcher to use Local runner with `CHROME_DEBUGGING_PORT` for H1-5/H1-7 to bypass Turnstile. | PASS if execution guide enforces engine topology matching anti-bot findings; FAIL if cloud recommended for admin. |
| **COMB-T3-09** | F5 (Local vs Fly) + F7 (RoE Rules) | Turnstile Anti-Bot Compliance & Hard-Stop Policy | Operational guardrail: DO NOT CLICK TURNSTILE / HCAPTCHA challenges. | When Turnstile appears on Fly.io, runner executes immediate hard-stop; zero automated solver scripts invoked. | PASS if hard-stop policy is strictly enforced upon Turnstile detection; FAIL if automated bypass attempted. |
| **COMB-T3-10** | F8 (Code Integrity) + F6 (CLI Guides) | Autonomous Execution Operates Exclusively via Existing Engine Tools | Verification that CLI execution guides utilize only the 6 existing MCP tools in `phantom_cloud.py`. | Guides introduce zero new tool dependencies or code modifications; tool calls adhere to unmodified server schemas. | PASS if execution guides are 100% compatible with frozen `phantom_cloud.py`; FAIL if new tools required. |

---

### Tier 4: Real-World Operational Scenarios (5 Comprehensive Walkthroughs)

#### Scenario 1: End-to-End Restricted Staff Differential Authorization Walkthrough (`SCEN-T4-01`)
- **Objective**: Conduct a complete, autonomous operational walkthrough verifying whether a merchant staff account restricted to viewing products can read or mutate sensitive order, customer, or financial data via internal GraphQL.
- **Preconditions**:
  - Local SSE runner active at `http://127.0.0.1:8000`.
  - Browser profile authenticated as `palabong+staff@wearehackerone.com` on Store A (`funk-it-up-sdzgxmea`).
- **Step-by-Step Walkthrough**:
  1. *Dispatch Tool Call 1 (`navigate`)*: Navigate to `https://admin.shopify.com/store/funk-it-up-sdzgxmea/orders`.
  2. *Dispatch Tool Call 2 (`wait`)*: Delay 4000ms for Polaris React hydration.
  3. *Dispatch Tool Call 3 (`get_snapshot mode="ax"`)*: Inspect Accessibility Tree. Assert presence of permission denial notice: `"You need permission to view this feature"`.
  4. *Dispatch Tool Call 4 (`evaluate`)*: Execute in-browser script to extract `<meta name="csrf-token">` and issue POST to `/admin/internal/web/graphql/core` requesting `orders(first: 5) { edges { node { id name } } }`.
  5. *Evaluate Assertion*: Assert that response returns `errors` containing `ACCESS_DENIED` and `data: null`.
  6. *Differential Verdict*: UI Denied + API Denied = **Secure Parity (No Differential Vulnerability)**.
- **Pass/Fail Semantics**: PASS if the entire 6-step lifecycle executes autonomously, logs exact response JSON, and asserts authorization parity; FAIL if tool fails or differential is misreported.

#### Scenario 2: Cross-Tenant Multi-Store Isolation Attack Simulation (`SCEN-T4-02`)
- **Objective**: Execute a rigorous multi-tenant cross-shop isolation attack evaluating whether Store A credentials can access, query, or inject objects into Store B.
- **Preconditions**:
  - Store A (`funk-it-up-sdzgxmea`) product ID `10323603521722` and variant `50535758364858` cataloged.
  - Store B (`xxxxxx-r48zg9i1`) active.
- **Step-by-Step Walkthrough**:
  1. *Dispatch Tool Call 1 (`navigate`)*: Navigate to Store B administrative URL `https://admin.shopify.com/store/xxxxxx-r48zg9i1/products` using Store A session.
  2. *Evaluate Assertion 1*: Assert HTTP 404, redirect to store switcher, or permission denied banner. Zero access to Store B product catalog.
  3. *Dispatch Tool Call 2 (`navigate`)*: Navigate to Store B storefront `https://xxxxxx-r48zg9i1.myshopify.com/products/the-hidden-snowboard`.
  4. *Evaluate Assertion 2*: Assert HTTP 404 Not Found (Store A handle unresolvable in Store B catalog partition).
  5. *Dispatch Tool Call 3 (`evaluate`)*: Dispatch AJAX POST to `https://xxxxxx-r48zg9i1.myshopify.com/cart/add.js` injecting Store A variant `{"items": [{"id": 50535758364858, "quantity": 1}]}`.
  6. *Evaluate Assertion 3*: Assert HTTP 422 Unprocessable Entity (`"Cannot find variant"`).
- **Pass/Fail Semantics**: PASS if all three attack vectors are completely rejected by Shopify's ambient database tenant scoping (`WHERE shop_id = ?`); FAIL if any cross-tenant data leaks.

#### Scenario 3: Storefront Primitive Exhaustion & Cart Drop Lifecycle Audit (`SCEN-T4-03`)
- **Objective**: Formally audit and verify the server-side cart drop lifecycle for unpurchasable hidden, draft, or archived products on Store A.
- **Preconditions**:
  - Store A product "The Hidden Snowboard" (`variant 50535758364858`) unpublished from sales channels.
- **Step-by-Step Walkthrough**:
  1. *Dispatch Tool Call 1 (`navigate`)*: Navigate to `https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard`.
  2. *Dispatch Tool Call 2 (`wait`)*: Delay 3000ms for theme DOM ready.
  3. *Dispatch Tool Call 3 (`get_snapshot mode="html"`)*: Identify Add to Cart button reference.
  4. *Dispatch Tool Call 4 (`click`)*: Click Add to Cart button.
  5. *Dispatch Tool Call 5 (`evaluate`)*: Fetch `/cart.js`. Assert `item_count === 0` and `total_price === 0`.
  6. *Dispatch Tool Call 6 (`navigate`)*: Navigate to `/checkout`.
  7. *Evaluate Assertion*: Verify that checkout redirects to `/cart` or displays flash notice: `"Some items in your cart became unavailable and were removed."`.
  8. *Closure Attestation*: Record formal verification that test data theme pricing does not permit financial transactions.
- **Pass/Fail Semantics**: PASS if server-side cart drop is verified end-to-end and documented as non-bountiable ($0); FAIL if cart permits checkout of dropped item.

#### Scenario 4: Dual-Engine Feasibility & Turnstile Evasion Operational Drill (`SCEN-T4-04`)
- **Objective**: Conduct a comparative operational drill evaluating the Local SSE runner against the remote Fly.io cloud engine to demonstrate Turnstile resistance dynamics.
- **Preconditions**:
  - Local SSE proxy active on `http://127.0.0.1:8000`.
  - Remote Fly.io engine deployed at `https://phantom-cloud-engine.fly.dev`.
- **Step-by-Step Walkthrough**:
  1. *Local Engine Verification*: Connect to Local SSE stream with token `ph_live_local_verify`. Navigate to `admin.shopify.com/store/funk-it-up-sdzgxmea`.
  2. *Local Evasion Assertion*: Assert page title reflects store admin, Turnstile challenge bypassed via residential IP + native GPU profile.
  3. *Remote Engine Drill*: Dispatch navigation to `https://accounts.shopify.com/login` via Fly.io SSE stream.
  4. *Remote Turnstile Assertion*: Capture page response. Assert title indicates Cloudflare interception (`Ci siamo quasi…` / `Just a moment...`).
  5. *Hard-Stop Protocol*: Verify that runner detects Turnstile challenge, refrains from automated clicking, and executes `HARD_STOP`.
  6. *Architectural Synthesis*: Validate the operational recommendation that authenticated testing must run on Local SSE runner.
- **Pass/Fail Semantics**: PASS if both local bypass and remote block are accurately demonstrated and hard-stop protocol verified; FAIL if runner hangs or attempts automated CAPTCHA click.

#### Scenario 5: Full Mission Autonomous CLI & Compliance Audit Routine (`SCEN-T4-05`)
- **Objective**: Execute an end-to-end autonomous mission verification incorporating pre-flight compliance checks, multi-tool MCP command dispatch, test logging, and core codebase integrity audit.
- **Preconditions**:
  - Clean git working tree; all strategy deliverables present in workspace.
- **Step-by-Step Walkthrough**:
  1. *Step 1: Pre-Flight Compliance Verification*: Execute automated audit confirming targets are strictly `funk-it-up-sdzgxmea` and `xxxxxx-r48zg9i1` owned by `palabong@wearehackerone.com`.
  2. *Step 2: MCP Tool Dispatch*: Sequentially dispatch test calls using all 6 approved tools (`navigate`, `get_snapshot`, `click`, `type`, `evaluate`, `wait`).
  3. *Step 3: Differential Log Generation*: Write structured JSON log to `artifacts/differential_run_audit.json`.
  4. *Step 4: PII Scrubbing Audit*: Inspect generated log file with regex scanner to confirm zero buyer PII is retained.
  5. *Step 5: Codebase Cryptographic Hash Audit*: Compute SHA-256 hashes of `phantom_cloud.py`, `Dockerfile`, `fly.toml`, and `requirements.txt`. Assert 100% bit-for-bit match with baseline hashes.
  6. *Step 6: Attestation Generation*: Output final test readiness attestation with exit code 0.
- **Pass/Fail Semantics**: PASS if all 6 steps execute cleanly, zero compliance violations occur, and codebase integrity is confirmed; FAIL on any violation.

---

## 5. Verification Matrix & Attestation Protocol

```
========================================================================================
                          E2E TEST SUITE VERIFICATION MATRIX
========================================================================================
 Tier   Category                           Minimum Req    Implemented    Status
----------------------------------------------------------------------------------------
 Tier 1 Feature Coverage (F1 to F9)            45             45         READY
 Tier 2 Boundary & Corner Cases (F1 to F9)     45             45         READY
 Tier 3 Cross-Feature Combinations              9             10         READY
 Tier 4 Real-World Operational Scenarios        5              5         READY
----------------------------------------------------------------------------------------
 Total  Comprehensive Verification Suite      104            105         VERIFIED READY
========================================================================================
```

*Architectural specification authored and verified by `test_writer_e2e`.*
