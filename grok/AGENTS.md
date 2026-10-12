PROJECT: phantom_cloud
STATUS: Lead-evaluation / all monetisation roads open
UPDATED: 2026-10-08T20:07Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
L0: grok/AGENTS.md
L1: grok/project_memory
L2: README.md
L2-arch: grok/phantom_cloud_architecture.md
PRODUCTION TREE: /Users/daniele_palagi/Desktop/phantom_cloud 2 (FROZEN)
INGEST REVISION: 2026-10-01T12:58Z
AUTHORITY: This file is the always-on constraint layer (L0). It is not the Project settings field.

═══════════════════════════════════════════════════════════════
0. INITIALISATION PATH (mandatory, every session)
═══════════════════════════════════════════════════════════════
Read in this order before any other file or action. Then reason against the production folder (read-only unless a path is named).

1. grok/AGENTS.md
1. grok/project_memory
1. README.md
2. grok/phantom_cloud_architecture.md

Do not skip step 2. Architecture is how the production tree is interpreted; README is schemas; memory is dated facts; this file is constraints.

Canonical L0 is grok/AGENTS.md only. Root artifacts/AGENTS.md was a pointer duplicate and is removed.

═══════════════════════════════════════════════════════════════
0a. INGEST MAP
═══════════════════════════════════════════════════════════════
| Layer | Path | When | What belongs here |
|-------|------|------|-------------------|
| L0 | grok/AGENTS.md | every turn | constraints, freeze, consult-scope |
| L1 | grok/project_memory | session start + after select-artifact change | dated facts, smoke index, Drive id. File has no .md twin. |
| L2 | README.md | before tool/auth/run work | wire schemas — READ ONLY |
| L2-arch | grok/phantom_cloud_architecture.md | after README, before engine reasoning | E2E / proxy / MCP lifecycle |
| L3 | reports/SMOKE.md + named run | before claiming production state | latest 6-tool acceptance — READ ONLY |
| L4 | runs/prod_postdeploy_/stealth_evaluation.md | before claiming stealth | caveats — READ ONLY |
| L5 | commercial/*.md | before commercial text | scope, RoE, fees — READ ONLY |
| L6 | VDP strategic document | before rewards/SLAs/platforms | Section 6 |

Conflict: L2 schemas, L2-arch runtime shape, L3 evidence, L1 dated facts, L0 constraints, L6 policy.
No invented tool surface.

Agent CLI prompt texts in grok/ are not L0.

═══════════════════════════════════════════════════════════════
0b. CONSULT SCOPE (mandatory)
═══════════════════════════════════════════════════════════════
NEVER grep, list, read, or consult any Grok local artifacts outside:
- grok/
- /Users/daniele_palagi/Desktop/phantom_cloud 2

unless the user authorizes another path in the same turn.

═══════════════════════════════════════════════════════════════
0c. PRODUCTION TREE FREEZE (mandatory)
═══════════════════════════════════════════════════════════════
NEVER create, edit, move, delete, or overwrite ANY path under /Users/daniele_palagi/Desktop/phantom_cloud 2 without an explicit user directive that names the path in the same turn.

Read-only consult of the production folder is required after the initialisation path.
Writes belong in grok/ unless the user names a production path.

Includes: phantom_cloud.py, Dockerfile, fly.toml, requirements.txt, tests/, runs/, reports/, commercial/, README.md, .env.example, .gitignore, smoke_test.py.

═══════════════════════════════════════════════════════════════
1. IDENTITY AND OBJECTIVE
═══════════════════════════════════════════════════════════════
phantom_cloud is a stealth browser MCP server (nodriver + Starlette/SSE). Phantom Architecture + AOM Distillation.

Objective: production-grade reliability and monetisation remain open in parallel. Phase as of 2026-09-28: evaluate new leads. No single shortest path is locked.
Open vectors (all active): invitational / public bug bounty research under program RoE; API/MCP access; managed continuous-security offerings; commercial pilot from commercial/ against 20260924 six-tool acceptance.
Engine freeze stands. Bounty leads do not authorize edits to phantom_cloud.py, Dockerfile, fly.toml, or requirements.txt.
Lead map: grok/leads/SCOPE_TRAIL_AND_OBJECTIVES_20260928.md.

Branch split:
- grok/ = strategy, memory, architecture note, CLI prompt text.
- Device Grok Build 4.7 on Drive folder 1msmuBIu_28tNkjBxhKQ6S-x9DzfZjpO5 = operative code / local test / Fly.
- CLI operative prompt does not load this L0 stack.

═══════════════════════════════════════════════════════════════
2. GROUND TRUTH
═══════════════════════════════════════════════════════════════
Runtime: Python 3.11+, nodriver, Starlette/SSE, uvicorn, Chrome, Xvfb. headless=False intentional.
Tools: navigate, get_snapshot (html|ax), click, type, evaluate, wait.
Auth: Unkey if UNKEY_ROOT_KEY set; else ph_live_. Wire: GET /sse/?token= ; POST /messages/t/<token>
Deploy: Fly.io phantom-cloud-engine, fra, https://phantom-cloud-engine.fly.dev, one machine. Live as of 2026-10-01T12:51Z: machine 78197e2be34d78, version 166, image deployment-01M3VR5JFXHPQCDF4E9CSGKGB9, Chrome 154.0.8037.92. Health before first session: browser_ready false. Operative channel: MCP Inspector http://127.0.0.1:6274 already on that Fly SSE. Do not cold-start a local engine for production smoke.
Latest 6-tool PASS: runs/prod_postdeploy_20260924T153949Z. Stealth eval 2026-09-23 PASS with caveats.
GitLab about:blank: runs/gitlab_matrix/HARD_STOP.txt
No Vercel AI Gateway on the operative CLI.

═══════════════════════════════════════════════════════════════
3. OPERATING RULES
═══════════════════════════════════════════════════════════════
- Facts first. Propose engine fixes only when asked.
- No invented certifications, SLAs, or contract vehicles.
- Do not recopy Drive .git, .venv, .pytest_cache, secrets, or live tokens.
- Do not paste L1–L6 into the Project settings field.
- Adaptation of this file is not approval to edit /Users/daniele_palagi/Desktop/phantom_cloud 2.
- CLI task inputs are not cold starts. No host inventory, no ingest replay, no restated wire tables unless the task asks.

═══════════════════════════════════════════════════════════════
4. SELECT-ARTIFACT ADAPTATION
═══════════════════════════════════════════════════════════════
When a select artifact changes, adapt THIS file in the same turn (pointers only). Writes only under grok/.

Select artifacts:
- grok/project_memory
- grok/phantom_cloud_architecture.md
- README.md
- reports/SMOKE.md
- commercial/PILOT_OFFER.md
- commercial/ROE_AND_SCOPE.md
- commercial/ONBOARDING_CHECKLIST.md
- commercial/PRICING_FRAME.md
- .env.example

Bump INGEST REVISION. Do not write the production tree.

═══════════════════════════════════════════════════════════════
5. RESPONSE STYLE
═══════════════════════════════════════════════════════════════
Institutional / technical / executive. State what changed and why. Shortest path to production or monetisation.
Answers to the user: Italian.
Generated prompts / CLI task inputs: English only.

CLI / operator task prompts are not cold starts. Emit only the commands and constraints required for that task. Do not restate host inventory, ingest map, or L0–L6. Do not wrap a six-tool smoke in a session-bootstrap brief.

═══════════════════════════════════════════════════════════════
6. ARTIFACT HEADER STAMP (mandatory on agent-owned files)
═══════════════════════════════════════════════════════════════
Every file written or revised under grok/ carries these three header fields near the top:

UPDATED: <ISO-8601 UTC>
VERSION: fly-<machine version> / git-<short sha> / ingest-<INGEST REVISION>
PROJECT: phantom_cloud

Current stamp: UPDATED 2026-10-08T20:07Z — VERSION fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
Production tree files are not restamped unless the user names the path.

END OF PERMANENT INSTRUCTIONS
