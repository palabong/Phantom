# Deploy phantom_cloud device dossier (Grok Build cwd = this repo)

You are Grok Build. CWD is the user's Drive production checkout of phantom_cloud
(folder id 1msmuBIu_28tNkjBxhKQ6S-x9DzfZjpO5). Title: env .env, Docker, Xvfb.

There is NO artifacts/.grok here. Do not look for a chat-sandbox L0.
Do not print .env, PHANTOM_AUTH_TOKEN, Unkey, or mcp.json token query strings.

## Goal

Create a scannable working-environment dossier inside THIS directory so another
operator (and a later Grok session) can see how this tree is run.

Create only these paths (mkdir as needed):

```
AGENTS.md
.grok/config.toml
.grok/agents/phantom-surgery.md
.grok/skills/phantom-matrix/SKILL.md
.grok/hooks/sessionstop-kill-idle.sh
.grok/DOSSIER.md
```

If `.mcp.json` or `~/.mcp-inspector/mcp.json` exists, READ to learn server names
and redact tokens in anything you write. Do not rewrite those secret files.

## 1. First: inventory (read-only)

List the repo root. Read if present: README.md, fly.toml, Dockerfile,
requirements.txt, tests/run_matrix_evaluation.py, reports/SMOKE.md,
.env.example, .gitignore. Note whether phantom_cloud.py / Docker / fly exist.
Do not open .env.

Record in DOSSIER.md: Python/Chrome/Xvfb/fly facts you can see from files,
six production MCP tools from README, latest smoke folder name if reports/ or
runs/ exist, and that SwiftShader is not claimed solved.

## 2. AGENTS.md (cwd — Grok will append this every session)

Max 3500 characters. Pointers only. No smoke tables.

Must include:
- This directory is the production engine checkout (Fly app phantom-cloud-engine, fra, https://phantom-cloud-engine.fly.dev).
- Tools: navigate, get_snapshot html|ax, click, type, evaluate, wait.
- Auth: Unkey or ph_live_; SSE /sse/?token=; messages /messages/t/<token>.
- Last snapshot mode owns refs (html e*, ax ax*). Never click e* after ax.
- Named-path discipline: do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt unless the user names the file.
- Do not dump secrets. Stop idle Chrome/Xvfb/local engine after tests.
- GitLab about:blank = hard stop.
- Latest 6-tool acceptance if SMOKE.md names it; else say unknown / read reports/SMOKE.md.
- Monetisation path: frozen engine + commercial/ pilot. Not this agent's job unless asked.

## 3. .grok/config.toml

Minimal project config only. Example shape — adapt to what inspect already has;
do not enable random MCP.

```toml
[agent]
name = "phantom-surgery"

[subagents]
enabled = false
```

If you discovered an MCP server URL for phantom-cloud-engine, add an
`[mcp_servers.phantom-cloud-engine]` block with url from config BUT replace any
token with `${PHANTOM_AUTH_TOKEN}` — never paste a live key.

## 4. .grok/agents/phantom-surgery.md

Official format: YAML camelCase frontmatter + short body.

```yaml
name: phantom-surgery
description: >
  Surgical edits on user-named files in this phantom_cloud production
  tree (especially tests/run_matrix_evaluation.py and dossier files).
  Do not use for engine/Fly/Docker/.env.
promptMode: extend
agentsMd: true
outputFormat: concise
permissionMode: default
tools:
  - read_file
  - search_replace
  - grep
  - list_dir
disallowedTools:
  - run_terminal_cmd
  - web_search
  - web_fetch
  - task
```

Body < 900 chars: named-path writes; AOM ref rule; no secret print; no fly
deploy; no inventing a 7th MCP tool; miss click is not a hit.

## 5. .grok/skills/phantom-matrix/SKILL.md

Frontmatter: name phantom-matrix; short description; when-to-use = matrix
evaluation / sannysoft / click ref stale / archive payloads.
user-invocable: true
disable-model-invocation: false

Body: required run order (html snap → type/click hit → miss → ax last);
archive files to write under runs/matrix_eval_<UTC>/; redact tokens;
sannysoft is not the 20260924 Next.js acceptance.

## 6. .grok/hooks/sessionstop-kill-idle.sh

Executable comment + script that pkill -f only local phantom_cloud.py /
Xvfb / google-chrome leftover from THIS project if possible. Safe no-op if
none. Do not register a hook in config unless you also add a
[[hooks]] SessionStop entry pointing at this script with a one-line comment
that the user must /hooks-trust. If hook schema is uncertain, write the
script only and document the trust step in DOSSIER.md — do not invent hook TOML.

## 7. .grok/DOSSIER.md  (the scan target)

This is the file a later agent reads first. Sections:

- Identity (cwd role, Fly hostname, region if fly.toml says so)
- Layout map (engine files vs tests vs reports vs runs vs commercial vs .grok)
- How to start Grok in this folder
  `grok --agent-profile .grok/agents/phantom-surgery.md --effort xhigh --no-subagents`
- MCP: how token is supplied (env PHANTOM_AUTH_TOKEN / inspector) — redacted examples only
- How to run the matrix runner (python command + env), not executed now
- AOM/click contract
- Protected files
- What is NOT in this tree (no chat-sandbox artifacts/.grok)
- Open gaps you observed (missing venv, missing Xvfb, runner not saving snapshot bodies, etc.)

No live tokens. No giant file dumps.

## Stop

Write the files. Run `grok inspect` if the binary works; paste a redacted
summary into DOSSIER.md. Do not start Chrome. Do not call Fly. Do not commit.
Do not create README.md if one exists. Do not touch the four protected engine files.
