One file: tests/run_matrix_evaluation.py
Do not touch phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.

Last get_snapshot mode owns the ref map (html=e*, ax=ax*). Never click e* after ax.
Parse refs from the html snapshot taken immediately before type/click. No hardcoded e1.
type N/A if no INPUT/TEXTAREA. Hit click: A|BUTTON else first e* else selector a[href].
Miss last: selector #phantom-missing-target; PASS on non trovato|not found.
Keep Fly SSE, token redact, sannysoft URL, wait 500, six-tool list, no body dumps.
Order: list → navigate → wait → html snap → scroll+text evaluate → type/click hit → scroll-top+stealth evaluate → html snap length → miss click → optional ax LAST.
search_replace only. Do not run the matrix. Do not commit.
