# Audit brief (emit in Italian, keep this structure)

Do not execute cleanup in the same turn as this brief.

## Hygiene audit

- cwd
- L0 path + INGEST REVISION
- cold-start already run this session (yes/no)
- audit script result (pass / findings count)
- objective lock (one line)

## Findings

Numbered list. Each item:

- class (P0–P3 / INFO)
- path
- why it reduces coherence
- proposed action (kill / patch-path / archive / delete / adapt-L0 / report-only)

## Keep set

Files that will not be touched.

## Cleanup plan

Numbered actions only. No extras.

## Gate

Ask for confirmation. Stop.
