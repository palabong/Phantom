---
name: phantom-matrix
description: >
  Run and archive the production 6-tool MCP matrix against bot.sannysoft.com
  via phantom-cloud-engine SSE. Use for matrix evaluation, sannysoft, stale
  click refs, and payload archives under runs/matrix_eval_/.
when-to-use: matrix evaluation / sannysoft / click ref stale / archive payloads
user-invocable: true
disable-model-invocation: true
---

Optional harness notes. Not project instructions. Prefer AGENTS.md and .grok/DOSSIER.md.

# Phantom matrix

Production SSE: `https://phantom-cloud-engine.fly.dev/sse/?token=${PHANTOM_AUTH_TOKEN}`.
Token from `PHANTOM_AUTH_TOKEN`, else `~/.mcp-inspector/mcp.json` server `phantom-cloud-engine` (do not rewrite that file). Target: `https://bot.sannysoft.com/`.

Sannysoft is not the 20260924 Next.js acceptance (`reports/SMOKE.md` / `runs/prod_postdeploy_20260924T153949Z`).

## Required run order

1. `tools/list` — exactly navigate, get_snapshot, click, type, evaluate, wait.
2. `navigate` then native `wait` (`delay_ms`).
3. `get_snapshot` `mode=html`. Capture `e*` refs from this body.
4. **Hit** — `type` if html has INPUT/TEXTAREA (else N/A); then `click` a **fresh** html ref. Refresh html snapshot immediately before the hit. Last snapshot mode owns refs.
5. **Miss** — `click` selector `#phantom-missing-target`. PASS if body matches `non trovato` / `not found` (often ~11s). Score FAIL from Italian error text even when `isError` is false.
6. **ax last** — Never click an e* ref that is not from the latest html snapshot. If ax runs, refresh html immediately before the click. Run ax before the hit only when that smoke order says so; do not run ax before the click when the user says not to. Never click `e*` after ax.

Connect 120s / SSE read 300s / ClientSession 180s. Trailing slash after `/sse/` is required.

## Archive

Matrix evaluation still writes runs/matrix_eval_<YYYYMMDDTHHMMSSZ>/. A production smoke writes a new runs/prod_postdeploy_<UTC>/ (do not overwrite) with SMOKE.md, protocol.json, network.json, html, ax, and evaluate.json. SMOKE.md columns Step / Tool, Result, Latency, Details are the 01a1137a requirement, not the matrix printer.

- `html_snapshot.txt`, `ax_snapshot.txt`, `evaluate.json`, `network.json`, `protocol.json`
- `MATRIX.md`, `ASSESSMENT.md`
- `payloads/` for click-hit and click-miss bodies

The printer-only harness in `tests/run_matrix_evaluation.py` currently logs lengths and truncated snippets; persist full bodies in the archive. Redact tokens (`abc...wxyz` or `REDACTED`). Do not copy another session’s snapshots into this folder.

Do not start a local engine, Chrome, or Xvfb unless the user names that path. Do not flyctl deploy and do not restart a machine that is already started unless the user asks. fly status and fly machine list are allowed. fly machine start only if machine 78197e2be34d78 is stopped. Deploy, when asked, is flyctl deploy --ha=false -a phantom-cloud-engine and belongs to phantom-fly, not this file.
