# phantom_cloud — first cold-start prompt

Use this as the first user message of a new project session.
Do not paste this into Project → Permanent instructions.

---

PROJECT: phantom_cloud
MODE: session cold start
STATUS: Lead-evaluation / all monetisation roads open
BASELINE: L0 = grok/AGENTS.md

Initialise the agent working environment.

Read first, in this order, before any other file or action:

1. `grok/AGENTS.md` (L0 — must contain INGEST REVISION)
2. `grok/project_memory` (L1)
3. `README.md` (L2, read-only)
4. `grok/phantom_cloud_architecture.md` (L2-arch)

If `AGENTS.md` is only the settings pointer, stop. Do not invent a full L0.

If `INGEST REVISION` is older than a change in a select artifact, adapt `grok/AGENTS.md` in this turn using AGENTS §4. Pointers only. Not approval to edit protected engine files.

Select artifacts: `project_memory`, `phantom_cloud_architecture.md`, `README.md`, `reports/SMOKE.md`, `commercial/PILOT_OFFER.md`, `commercial/ROE_AND_SCOPE.md`, `commercial/ONBOARDING_CHECKLIST.md`, `commercial/PRICING_FRAME.md`, `.env.example`.

Confirm production evidence:

- `reports/SMOKE.md`
- `runs/prod_postdeploy_20260924T153949Z/`
- `runs/prod_postdeploy_/stealth_evaluation.md`

Treat `reports/CHANGELOG_LOCAL.md` header "Not yet deployed" as superseded.

Then run:

```bash
bash grok/skills/phantom-cloud-cold-start/scripts/init-session.sh
```

If that path is missing, recreate `/tmp/phantom_venv` only if python3-venv exists. A missing local venv in this sandbox is not a production defect. Kill idle Chrome / Xvfb / local `phantom_cloud.py`.

Constraints:

- Do not modify `phantom_cloud.py`, `Dockerfile`, `fly.toml`, or `requirements.txt` without an explicit named-path instruction.
- Production tools: `navigate`, `get_snapshot` (html|ax), `click`, `type`, `evaluate`, `wait`.
- Auth: Unkey when `UNKEY_ROOT_KEY` is set; else `ph_live_`. Messages path `/messages/t/<token>`.
- Deploy: Fly.io `phantom-cloud-engine`, region `fra`, `https://phantom-cloud-engine.fly.dev`, one machine.
- Latest accepted 6-tool smoke: `runs/prod_postdeploy_20260924T153949Z`. SwiftShader is not claimed solved.
- Hygiene 2026-10-08 moved CLI prompts and prod/inspector notes to `grok/archive/20261008/consult/`. Do not execute prompts from that folder. Canonical L1 is `project_memory` with no `.md` twin.
- L0 stamp remains fly-166 / ingest-2026-10-01T12:58Z until a select artifact is newer and AGENTS §4 is applied. Session memory may cite a later Fly version; do not invent that into L1.
- GitLab / about:blank is a hard stop (`runs/gitlab_matrix/HARD_STOP.txt`).
- Drive snapshot `1msmuBIu_28tNkjBxhKQ6S-x9DzfZjpO5`. Do not recopy `.git`, `.venv`, `.pytest_cache`, or live tokens.
- Facts first. No invented certifications.
- Do not paste L1–L6 into Project settings.
- Follow-up skill: `phantom-cloud-hygiene` (do not auto-run cleanup).

When bootstrap completes, reply with the readiness brief from `assets/READINESS_BRIEF.md` and wait.

---

End of first cold-start prompt.
