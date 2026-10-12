UPDATED: 2026-10-06T23:34Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — fix the broken smoke flow

Paste into the device Grok Build terminal. Web UI driving is the broken path. `--cli` is the fix.

```
CWD: "/Users/daniele_palagi/Desktop/phantom_cloud 2"

The broken flow is fixed only by not using the browser. Grok Build cannot see http://127.0.0.1:6274. Do not open that page. Do not write a Python client. Do not run smoke_test.py or execute_task.py. Do not edit phantom_cloud.py, Dockerfile, fly.toml, or requirements.txt. Do not fly deploy. Do not restart machine 78197e2be34d78. Do not print a token. Redact every secret to [REDACTED].

Already true at 2026-10-06T23:19Z: machine started, version 192, image phantom-cloud-engine:deployment-01M49M4AM14QB0SMXE3624KX25. Inspector pid 14128. tools/list returned navigate, get_snapshot, click, type, evaluate, wait.

1. Read the Fly SSE URL from /private/tmp/phantom-inspector.log or from the Inspector config already used by pid 14128. Do not read execute_task.py. Keep the token in a shell variable. Do not echo it.
2. Run the official client, not the web UI:
   npx --yes @modelcontextprotocol/inspector --cli "<sse url>" --transport sse --method tools/list --format json
   If --transport sse is rejected, stop and quote the error. Do not invent another client.
3. On that same client, one call each, --format json. Navigate timeout is at least 60s.
   tools/call navigate url=https://bot.sannysoft.com/
   tools/call wait delay_ms=500
   tools/call get_snapshot mode=html
   tools/call get_snapshot mode=ax
   tools/call evaluate expression=JSON.stringify({title:document.title,href:location.href,webdriver:navigator.webdriver,ua:navigator.userAgent})
   type: N/A if the html snapshot has no input
   tools/call click ref=<eN from that html snapshot>
   tools/call click selector=#phantom-missing-target
4. Archive only under runs/prod_postdeploy_<UTC>/ as SMOKE.md, protocol.json, html_snapshot.txt, ax_snapshot.txt, evaluate.json. Redact tokens before writing. click_miss PASSes only on the controlled missing-selector error.

Reply: archive path, matrix, evaluate JSON. Stop.
```
