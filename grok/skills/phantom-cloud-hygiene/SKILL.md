---
name: phantom-cloud-hygiene
description: Full hygiene audit and gated cleanup of the phantom_cloud working environment after phantom-cloud-cold-start. Use at session hygiene, workspace cleanup, drift check, post-bootstrap, or when asked to optimise the agent environment before coherent production or monetisation work. Always ask confirmation before any cleanup.
metadata:
  type: workflow
  version: "1.0"
  after: phantom-cloud-cold-start
---

# Phantom Cloud Hygiene

## Overview

Run after `phantom-cloud-cold-start`. Audit the agent workspace against canonical L0, surface drift and stale interventions, then stop. Cleanup runs only after explicit user confirmation. Goal — a lean, current working set so later answers stay aligned with production-path / monetisation-priority.

## Hard constraints (never waive)

- L0 is `grok/AGENTS.md`. Not `.grok/`.
- Writes only under `grok/` unless the user names another path in the same turn.
- Do not create, edit, move, or delete anything under `` during hygiene.
- Protected even inside `.grok/`: `AGENTS.md`, `project_memory`, `phantom_cloud_architecture.md`. Propose pointer adaptations only (AGENTS §4).
- Do not recopy Drive `.git`, `.venv`, `.pytest_cache`, secrets, or live tokens.
- Do not invent certifications, SLAs, or a solved SwiftShader.
- Dated facts in `project_memory` change only with a same-turn green light.
- Answers to the user in Italian. Generated prompts in English.
- Consult scope remains `grok/` and `` only.

## Sequence (mandatory)

1. If cold-start has not run this session, load and run `phantom-cloud-cold-start` first. Do not skip L0 → L1 → L2 README → L2-arch.
2. Read `references/hygiene-doctrine.md` then run `scripts/hygiene-audit.sh`. Do not skip the script.
3. Refresh objectives from L0 §1, L1 monetisation vectors, and headlines only of `commercial/PILOT_OFFER.md`, `ROE_AND_SCOPE.md`, `PRICING_FRAME.md`, `ONBOARDING_CHECKLIST.md` (read-only).
4. Classify every finding with `references/findings-taxonomy.md`.
5. Emit the audit brief from `assets/AUDIT_BRIEF.md`. Include a numbered cleanup plan. Then stop and wait.
6. Ask confirmation with the options in `assets/CONFIRMATION.md`. Do not delete, move, or rewrite until the user answers.
7. After confirmation, execute only approved items. Write `grok/HYGIENE_<UTC>.md` using `assets/HYGIENE_REPORT.md` and the L0 header stamp (UPDATED / VERSION / PROJECT).
8. Reply with the post-cleanup brief. Wait for the next task.

## What hygiene may propose

Safe to propose (still gated):

- Kill idle local `phantom_cloud.py` / Chrome / Xvfb (same policy as cold-start).
- Recreate `/tmp/phantom_venv` only if `python3-venv` exists. A missing sandbox venv is not a production defect.
- Archive or delete **agent-owned** clutter under `grok/` that is superseded, duplicate, or off-objective (example — `project_memory.md` stub vs canonical `project_memory`).
- Adapt L0 pointers only when a select artifact is newer than `INGEST REVISION` (AGENTS §4).
- Align custom skill path strings that still point at `.grok/` or root `artifacts/AGENTS.md` as L0.

Never propose:

- Edits to `phantom_cloud.py`, `Dockerfile`, `fly.toml`, `requirements.txt`, tests, runs, reports, commercial files, README, `.env.example`.
- Marking SwiftShader solved.
- Pasting L1–L6 into Project settings.
- Expanding consult scope outside `.grok/` + `phantom_cloud/`.

## Audit surface

| Area | Canonical | Drift to flag |
|------|-----------|---------------|
| L0 | `grok/AGENTS.md` | Missing INGEST REVISION; skill/script still treating root `artifacts/AGENTS.md` or `phantom_cloud/.grok/` as L0 |
| L1 | `grok/project_memory` | Twin `project_memory.md`; facts newer than green light |
| L2 / L2-arch | README + `phantom_cloud_architecture.md` | Architecture stamp behind live machine/version in L1 |
| L3 / L4 | `reports/SMOKE.md`, `runs/prod_postdeploy_20260924T153949Z/`, stealth eval | Claiming a newer smoke as the accepted 6-tool baseline without L1 update |
| Agent files | `grok/*` | Missing header stamp; one-shot prompts that duplicate a later dossier; files unused by current objective |
| Skills | `grok/skills/phantom-cloud-*` | Path doctrine out of date vs L0 |
| Runtime | `/tmp/phantom_venv`, Chrome, Xvfb | Idle browsers; broken venv claimed as prod failure |
| Scope | `.grok/` + `phantom_cloud/` | Reads or writes outside consult scope |

## Confirmation gate

Until the user confirms, hygiene is read-only plus the audit brief.

Accepted confirmations:

- `all` — execute the numbered plan as listed
- `only N,M,...` — execute those item numbers
- `none` / `report-only` — write the report, change nothing
- a rewritten plan — treat the rewrite as the approved set

If the user is silent, wait. Do not infer yes.

## Current objective lock (refresh every run)

Status — lead-evaluation. All monetisation roads open as of 2026-09-28.

Open in parallel — first-party H1 research under live program RoE; invitational / continuous-security services; API/MCP access; managed offerings; commercial pilot against `runs/prod_postdeploy_20260924T153949Z`.

Lead map — `grok/leads/SCOPE_TRAIL_AND_OBJECTIVES_20260928.md`.

Tool surface — `navigate`, `get_snapshot` (html|ax), `click`, `type`, `evaluate`, `wait`.

Deploy — Fly `phantom-cloud-engine`, `fra`, `https://phantom-cloud-engine.fly.dev`, one machine.

Engine freeze stands. Do not reopen engine surgery unless the user names a production path.
