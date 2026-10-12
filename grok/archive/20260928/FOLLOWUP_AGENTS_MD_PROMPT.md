# Follow-up: project instructions only

CWD is /Users/daniele_palagi/Desktop/phantom_cloud (trusted).

A previous pack left a project skill that is a test playbook. Project instructions are 0 because AGENTS.md is missing. Fix that gap. Do not rebuild a matrix report.

## Read

`.grok/DOSSIER.md` (source of truth). README.md tool list only if a schema line is missing from the dossier.

Do not read runs/. Do not open .env. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.

Plan, memory, fetch, and a subagent (task) are allowed if they help draft AGENTS.md from the dossier. They must not expand scope: no engine edits, no new skills/hooks, no matrix pack restore. Fetch only README/docs already in-tree or public xAI CLI trust docs if a flag name is uncertain.

## Write

1. Create `AGENTS.md` in the workdir root (this is what grok inspect counts as project instructions).

Copy constraints from the dossier, short:
- This cwd is the production engine checkout (Fly app / hostname from dossier).
- Scan `.grok/DOSSIER.md` first.
- Six tools only; last snapshot mode owns e* / ax*; click ref > selector > x,y.
- Auth /sse/?token= and /messages/t/<token>; trailing slash on /sse/.
- Named-path discipline on the four protected files.
- No secret dump. No fly deploy unless asked.
- Evidence pointer: reports/SMOKE.md and the archive that file names. runs/ is telemetry.
- Do not describe any single test archive or target site.

Cap 80 lines. No PASS tables. No skill playbook.

2. If `.grok/skills/phantom-matrix/SKILL.md` exists: set
   `disable-model-invocation: true`
   and first body line: "Optional harness notes. Not project instructions. Prefer AGENTS.md and .grok/DOSSIER.md."
   Do not delete unless the user already asked to delete.

Do not add agents, hooks, or a second dossier. Do not rewrite `.grok/DOSSIER.md` except one sentence under Grok CLI: "AGENTS.md is present; inspect project instructions should be > 0 after trust."

## Stop

Re-read AGENTS.md. If it names a matrix archive or sannysoft as the job, strip that. Do not run tests. Do not commit.
