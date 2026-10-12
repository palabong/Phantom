# Architecture + CLI settings dossier

A previous CLI pass built a test-driven working pack (dossier, skill, and related session copies) around one harness run. That path was wrong. Those generated files were deleted on both the operator device and the chat sandbox. Do not look for them. Do not restore them. Do not name them. Start from the production tree as it is now.

You are Grok Build. CWD is this phantom_cloud checkout (Desktop or Drive-synced copy).

## Goal

Write `.grok/DOSSIER.md` as the operator map of:
1. System architecture (what runs where)
2. Grok CLI settings for THIS workdir

Not a test report. Not an assessment of any `runs/` folder.

## Allowed reads

README.md, fly.toml, Dockerfile, requirements.txt, .env.example, .gitignore,
AGENTS.md if present, `.grok/config.toml` if present, commercial/ names only.
`grok inspect` if the binary works.

Do not open .env. Do not read `runs/` or `reports/` bodies. Do not edit
phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.

## Write

Create `.grok/` if missing. Write ONLY `.grok/DOSSIER.md`.
Do not add agents, skills, hooks, or extra markdown.

If AGENTS.md or `.grok/config.toml` already exist, leave them unless a single
line blocks CLI use.

## DOSSIER.md headings

1. Identity — stealth-browser MCP; Fly app, region, hostname from fly.toml/README; scale/SSE affinity only if fly.toml states it.
2. Runtime — Python / Chrome / Xvfb from Dockerfile and README; env *names* from .env.example only.
3. Request path — GET `/sse/?token=` (trailing slash required) → POST `/messages/t/<token>`; Unkey when UNKEY_ROOT_KEY set, else `ph_live_`.
4. Production tool surface — navigate; get_snapshot html|ax (html → e*, ax → ax*); click ref > selector > x,y; type; evaluate; wait. Last snapshot mode owns refs. Six tools. No seventh.
5. Repo layout — engine, tests, reports, runs, commercial, .grok. Protected: phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
6. Grok CLI in this workdir —
   - default start: `grok --effort xhigh --no-subagents --disable-web-search`
   - if a project agent file exists under `.grok/agents/`, document `--agent-profile` for that path; do not invent one
   - project `.grok/config.toml` applies `[mcp_servers]`, `[plugins]`, `[permission]`, `[mcp]` only
   - folder trust required before AGENTS.md / project skills load
   - MCP URL if configured: token via `${PHANTOM_AUTH_TOKEN}` only
   - redacted `grok inspect` summary (trusted yes/no, MCP names, no secrets)
7. Evidence index — at most three bullets: `reports/SMOKE.md` and the archive *that file* names; `runs/` is telemetry not the CLI contract. No run narrative.
8. Out of scope — do not copy chat-sandbox trees; do not dump secrets; do not fly deploy.

Cap 250 lines. No latency tables. No PASS/ERROR matrices. No target-site playbooks.

## Stop

Write DOSSIER.md. Re-read. If the file describes a specific test archive or a
deleted skill/agent pack, strip that text. Do not run the engine. Do not commit.
