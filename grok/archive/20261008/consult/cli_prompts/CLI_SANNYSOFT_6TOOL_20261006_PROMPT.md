UPDATED: 2026-10-06T21:56Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — full 6-tool Sannysoft smoke, archive only

Paste the block below into the device Grok Build terminal. Do not fly-deploy. Do not edit the engine.

```
CWD: /Users/daniele_palagi/Desktop/phantom_cloud
Production only. Inspector http://127.0.0.1:6274 is already on https://phantom-cloud-engine.fly.dev SSE.
Machine 78197e2be34d78. Do not restart it. Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt. Do not start a local engine on :8000.
One SSE. Token stays in the Inspector address. Do not print it. Redact it in every saved file.
Do not claim SwiftShader solved. Do not click Turnstile / hCaptcha. Do not open any URL except https://bot.sannysoft.com/.
The 2026-10-06T21:52Z Inspector export is not acceptance: it exercised navigate and html get_snapshot only.

Run this sequence on the live Inspector session. Record each JSON-RPC result, duration, and isError.

1. tools/list
2. navigate {"url":"https://bot.sannysoft.com/"}
3. wait {"delay_ms":500}
4. get_snapshot {"mode":"html"}
5. get_snapshot {"mode":"ax"}
6. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,webdriver:navigator.webdriver,ua:navigator.userAgent,vendor:navigator.vendor})"}
7. type — N/A if the html snapshot has no input. If an input ref exists, type {"ref":"<that ref>","text":"PHANTOM-TRACE-9901","clear":true}. Do not type into a token or password field.
8. click {"ref":"<eN from the html snapshot immediately before this call>"}
9. click {"selector":"#phantom-missing-target"}

Archive only. UTC stamp from the navigate response. Write these files and nothing else:

runs/prod_postdeploy_<UTC>/SMOKE.md
runs/prod_postdeploy_<UTC>/protocol.json
runs/prod_postdeploy_<UTC>/network.json
runs/prod_postdeploy_<UTC>/html_snapshot.txt
runs/prod_postdeploy_<UTC>/ax_snapshot.txt
runs/prod_postdeploy_<UTC>/evaluate.json

SMOKE.md matrix columns: Step / Tool, Result, Latency, Details. Rows: tools/list, navigate, wait, get_snapshot_html, get_snapshot_ax, evaluate, type or type_na, click, click_miss. PASS only if isError is false, except click_miss which PASSes on the controlled missing-selector error. Copy UA and WebGL vendor/renderer strings as observed. Do not infer machine version from the UA major.

Reply: archive path, matrix, evaluate JSON. Stop.
```
