# Hygiene doctrine

Canonical L0 is `/Users/daniele_palagi/Desktop/phantom_cloud 2/grok/AGENTS.md`.
Canonical L1 is `/Users/daniele_palagi/Desktop/phantom_cloud 2/grok/project_memory` (no `.md` twin required).
L2 README is read-only under the production tree.
L2-arch is `/Users/daniele_palagi/Desktop/phantom_cloud 2/grok/phantom_cloud_architecture.md`.

Root `/workspace/artifacts/AGENTS.md` is a five-line settings pointer. It is not L0.
`.grok/` is not the agent home. Do not create it during hygiene.

## Why hygiene exists

Cold-start loads constraints. Hygiene removes drift so the next task does not reason from stale paths, duplicate memory files, leftover one-shot prompts, or idle browsers.

## Write policy

| Location | Hygiene may write after confirm? |
|----------|----------------------------------|
| `grok/` agent-owned files | Yes, if listed in the approved plan |
| `grok/AGENTS.md` | Pointers only, AGENTS §4, select artifact newer than INGEST REVISION |
| `grok/project_memory` | Only with same-turn green light |
| `**` | Never |
| `grok/skills/phantom-cloud-*` | Yes, path-alignment only, if approved |
| `/tmp/phantom_venv` | Yes, recreate if python3-venv exists |

## Header stamp (every new/revised file under grok/)

```
UPDATED: <ISO-8601 UTC>
VERSION: fly-<ver> / git-<sha> / ingest-<INGEST REVISION>
PROJECT: phantom_cloud
```

Copy VERSION from current L0. Do not invent a new fly/git id.

## Language

User-facing briefs — Italian.
Skill assets and generated CLI prompts — English.
