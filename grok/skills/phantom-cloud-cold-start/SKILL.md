---
name: phantom-cloud-cold-start
description: Initialise a new phantom_cloud agent session against canonical L0 under artifacts/.grok. Use at session start, cold start, bootstrap, or when asked to set up the working environment. Loads AGENTS then project_memory then README then architecture, runs init-session.sh, emits a readiness brief, then waits. Does not run hygiene cleanup.
metadata:
  type: workflow
  version: "1.2"
  next: phantom-cloud-hygiene
---

# Phantom Cloud Cold Start

## Overview

Bootstrap a phantom_cloud analysis session. Load constraints and evidence, probe runtime, emit a readiness brief, then wait. Do not edit the production tree. Do not auto-run hygiene cleanup.

## Hard constraints (never waive)

- L0 is `grok/AGENTS.md`. Not `.grok/`. Not root `artifacts/AGENTS.md` (pointer only).
- L1 is `grok/project_memory` (no required `.md` twin).
- L2 README is read-only under `README.md`.
- L2-arch is `grok/phantom_cloud_architecture.md`. Do not skip it.
- Writes only under `grok/` unless the user names another path in the same turn.
- Do not create `.grok/`.
- Protected production files — `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt` — plus tests, runs, reports, commercial, README, `.env.example`.
- Consult scope — `grok/` and `` only, unless the user authorizes another path in the same turn.
- Facts first. No invented certifications, SLAs, or a solved SwiftShader.
- Dated facts in `project_memory` change only with a same-turn green light.
- Answers to the user in Italian. Generated prompts in English.
- No live tokens in briefs or agent files.

## Sequence (mandatory)

1. Read `references/doctrine.md`.
2. Read in order — L0 `grok/AGENTS.md`, L1 `grok/project_memory`, L2 `README.md`, L2-arch `grok/phantom_cloud_architecture.md`.
3. If L0 is only the settings pointer (no `INGEST REVISION`), stop and say so. Do not invent a full L0.
4. If a select artifact is newer than `INGEST REVISION`, adapt `grok/AGENTS.md` pointers only (AGENTS §4). Adaptation is not approval to edit the production tree.
5. Confirm L3/L4 evidence exists — `reports/SMOKE.md`, `runs/prod_postdeploy_20260924T153949Z/`, `runs/prod_postdeploy_/stealth_evaluation.md`. Treat `CHANGELOG_LOCAL.md` “not yet deployed” as superseded.
6. Run `scripts/init-session.sh`. Do not skip it.
7. Emit the readiness brief from `assets/READINESS_BRIEF.md`. Then wait.
8. Next skill (do not auto-run) — `phantom-cloud-hygiene` when the user asks for hygiene, drift check, workspace cleanup, or to optimise the working environment. Hygiene stays read-only until the user confirms.

## Select artifacts (adaptation trigger)

- `grok/project_memory`
- `grok/phantom_cloud_architecture.md`
- `README.md`
- `reports/SMOKE.md`
- `commercial/PILOT_OFFER.md`
- `commercial/ROE_AND_SCOPE.md`
- `commercial/ONBOARDING_CHECKLIST.md`
- `commercial/PRICING_FRAME.md`
- `.env.example`

## Runtime notes

- Local venv — `/tmp/phantom_venv` (artifacts FS cannot hold venv symlinks). A missing sandbox venv is not a production defect.
- Stop idle local `phantom_cloud.py` / Chrome / Xvfb during init.
- Tools — `navigate`, `get_snapshot` (html|ax), `click`, `type`, `evaluate`, `wait`.
- Auth — Unkey when `UNKEY_ROOT_KEY` is set; else `ph_live_`. Messages path `/messages/t/<token>`.
- Deploy — Fly `phantom-cloud-engine`, `fra`, `https://phantom-cloud-engine.fly.dev`, one machine.
- Accepted 6-tool smoke — `runs/prod_postdeploy_20260924T153949Z`.
- GitLab / `about:blank` — hard stop (`runs/gitlab_matrix/HARD_STOP.txt`).

## Current objective lock (refresh from L0 every run)

Copy status from L0 §1. As of 2026-09-28 — lead-evaluation, all monetisation roads open. Engine freeze stands. Lead map — `grok/leads/SCOPE_TRAIL_AND_OBJECTIVES_20260928.md`.

## State after hygiene 2026-10-08T18:53Z

- L0 unchanged: INGEST REVISION 2026-10-01T12:58Z, VERSION fly-166 / git-6e95b31. L1 file not edited.
- Consult set (not live inputs): `grok/archive/20261008/consult/` — twins, 27 CLI prompts, 6 prod/inspector notes. Index in that folder.
- This agent sandbox had no `` tree. Missing L2/L3 here is a mount gap, not a failed deploy.
- Accepted 6-tool baseline remains `runs/prod_postdeploy_20260924T153949Z` when the production tree is mounted. Later Sannysoft/Inspector notes are not that baseline.
- Session memory, not restamped into L1: Fly machine 78197e2be34d78 version 193 claimed 2026-10-07; H1 store B cart class closed on beanie and black-sunnies; H1-7 cross-store variant 422, not a draft. H1-2 still needs a same-turn staff secret.
- Do not treat `project_memory.md` as L1 if it reappears.

## Resources

- `assets/READINESS_BRIEF.md`
- `assets/COLD_START_PROMPT.md` (first-message template; keep paths aligned with this SKILL.md)
- `references/doctrine.md`
- `scripts/init-session.sh`
- follow-up — `grok/skills/phantom-cloud-hygiene/`
