UPDATED: 2026-10-01T12:58Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — production Sannysoft smoke

CWD: `/Users/daniele_palagi/Desktop/phantom_cloud`
Production only. Inspector `http://127.0.0.1:6274` already on `https://phantom-cloud-engine.fly.dev`.
Machine `78197e2be34d78`, version 166, image `deployment-01M3VR5JFXHPQCDF4E9CSGKGB9`. Do not restart it. Do not deploy. Do not edit engine files. Do not start a local engine on `:8000`.
One SSE. Token stays in the Inspector address. Do not print it.
Do not claim SwiftShader solved. Do not click Turnstile / hCaptcha.

1. tools/list
2. navigate {"url":"https://bot.sannysoft.com/"}
3. wait {"delay_ms":500}
4. get_snapshot {"mode":"html"}
5. get_snapshot {"mode":"ax"}
6. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,webdriver:navigator.webdriver,ua:navigator.userAgent})"}
7. type — N/A if the html snapshot has no input
8. click {"ref":"<eN from the html snapshot immediately before>"}
9. click {"selector":"#phantom-missing-target"}

Archive: `runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,network.json,html_snapshot.txt,ax_snapshot.txt,evaluate.json}`
Reply: path, matrix, evaluate JSON. Stop.
