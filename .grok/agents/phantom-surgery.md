---
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
---

Write only files the user names (often `tests/run_matrix_evaluation.py` and `.grok/*`). Leave `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`, and `.env` untouched unless named.

Last `get_snapshot` mode owns refs: html `e*`, ax `ax*`. Refresh snapshot immediately before a ref click/type. Never click `e*` after ax. A miss on `#phantom-missing-target` with "non trovato"/"not found" is a controlled PASS.

Never print tokens, Unkey keys, or `.env` values. Redact as `abc...wxyz` or `${PHANTOM_AUTH_TOKEN}`.

No `fly deploy`, no inventing a 7th MCP tool. Production surface is six tools. After local tests, stop leftover `phantom_cloud.py` / Xvfb / `google-chrome-stable`. GitLab `about:blank` is a hard stop.

Read `.grok/DOSSIER.md`. Matrix work: `.grok/skills/phantom-matrix/SKILL.md`.
