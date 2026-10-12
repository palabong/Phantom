# Findings taxonomy

Assign every finding a class and a default action. The default action is a proposal, not an execute order.

| Class | Meaning | Default proposal |
|-------|---------|------------------|
| P0-RUNTIME | Idle Chrome / Xvfb / local engine that can leak state into the next task | Kill listed PIDs |
| P1-CANON | Skill or script treats the wrong file as L0/L1 | Patch path strings in the named skill/script |
| P1-DUP | Duplicate fact store (`project_memory.md` vs `project_memory`) | Remove or archive the non-canonical twin |
| P2-STALE | Agent file whose objective is superseded by a later dossier or by the frozen-engine lock | Archive under `grok/archive/` or delete if user chooses delete |
| P2-STAMP | Agent file missing UPDATED / VERSION / PROJECT | Add stamp only if the file stays; skip archives |
| P3-INGEST | Select artifact newer than L0 INGEST REVISION | Adapt AGENTS.md pointers only |
| P3-FACT | L1 fact conflicts with L3 evidence | Report only unless user green-lights a memory edit |
| INFO | Missing local venv, missing Xvfb in sandbox, CHANGELOG_LOCAL superseded header | Note. Not a production defect |

## Keep set (never archive or delete)

- `grok/AGENTS.md`
- `grok/project_memory`
- `grok/phantom_cloud_architecture.md`
- Production tree files
- Accepted smoke and stealth archives under `runs/` and `reports/`

## Archive convention

If the approved plan says archive:

```
grok/archive/YYYYMMDD/<original-basename>
```

Create `archive/` only after confirmation. Do not invent a parallel top-level folder.
