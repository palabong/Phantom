# Integrate missing matrix-report artifacts

CWD is the Drive phantom_cloud production tree (or artifacts/phantom_cloud). Named files only.

## Source of gaps

Archive matrix_eval_20260926T155739Z / ASSESSMENT.md "Missing artifacts":
- html_snapshot.txt (14829 B claimed, snippet only)
- ax_snapshot.txt (59531 B claimed, not saved)
- evaluate.json (178 B stealth JSON, not saved)
- navigate / wait / evaluate scroll-down / text-check / scroll-top bodies (lengths only)
- network.json (never written)

Also: click {ref:e1} ERROR because html snap then ax then click e* from stale snap1. Miss PASS is not a hit.

## Edit these paths only

1. tests/run_matrix_evaluation.py
2. Create tests/matrix_eval_writer.py ONLY if the runner already expects a helper; otherwise keep write logic inside the runner. Prefer one file.

Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt, commercial/, reports/SMOKE.md, .env.

## Runner behavior to add

On each run, mkdir runs/matrix_eval_<UTC>/payloads/ and write:

| File | Source |
|---|---|
| payloads/html_snapshot.txt | full text of first get_snapshot html |
| payloads/ax_snapshot.txt | full text of get_snapshot ax (ax AFTER hit+miss) |
| payloads/html_snapshot_final.txt | full text of final html snap |
| payloads/evaluate_scroll_down.txt | evaluate scroll-down body |
| payloads/evaluate_text_check.txt | evaluate Broken Image Dimensions body |
| payloads/evaluate_scroll_top.txt | evaluate scroll-top body |
| payloads/evaluate.json | stealth evaluate JSON (parse if valid JSON, else raw string under key raw) |
| payloads/navigate.txt | navigate body |
| payloads/wait.txt | wait body |
| payloads/click_hit.txt | hit click response |
| payloads/click_miss.txt | miss click response |
| protocol.json | existing step list + payload_captured true and relative paths |
| MATRIX.md | table + list of saved files and byte sizes |
| ASSESSMENT.md | quality / validity / errors / missing (missing must be empty if writes succeeded) |
| console.log | same prints as now |
| network.json | {"captured":false,"reason":"no production MCP network tool"} — do not invent packets |

Redact TOKEN everywhere in written files (existing redact()).

Keep snippet print at 100 chars. Also persist full bodies.

## Click/type order (still required)

list → navigate → wait → html snap (SAVE) → scroll+text evaluate (SAVE) → type from THAT html (N/A if no INPUT/TEXTAREA) → click hit from parsed e* on THAT html (A\|BUTTON else first e* else selector a[href]) → scroll-top + stealth evaluate (SAVE evaluate.json) → html snap final (SAVE) → click miss selector → get_snapshot ax LAST (SAVE). Never click e* after ax. No hardcoded e1.

## MATRIX.md / ASSESSMENT.md

MATRIX: every step Result / Latency / Payload bytes / payload filename.
ASSESSMENT: do not say "body not saved" for files you now write. State click-hit uses live html map. Miss PASS remains controlled not-found. Do not call this L3 20260924 Next.js acceptance. SwiftShader not solved.

## Stop

Do not run the matrix against Fly. Do not commit. Do not print secrets.
search_replace / write the named test file(s). Re-read the runner once and confirm save paths + order.
