UPDATED: 2026-10-06T22:34Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# CLI — Inspector session-token URL investigation

Paste the block below into the device Grok Build terminal. Diagnostic only.

```
CWD: /Users/daniele_palagi/Desktop/phantom_cloud

Investigate only why launching MCP Inspector no longer presents a session URL of the form http://127.0.0.1:6274/?MCP_INSPECTOR_API_TOKEN=<rotating>. Do not run a smoke. Do not call Fly. Do not navigate. Do not write a client. Do not open /tmp/ph_smoke.py. Do not run smoke_test.py or execute_task.py. Do not print, grep, or copy any token value. Redact every secret to [REDACTED] before writing.

Report these facts, each with the command or file that produced it:

1. Which binary answers `mcp-inspector` and `npx @modelcontextprotocol/inspector`. Package version. Node version. v1 used MCP_PROXY_AUTH_TOKEN and a proxy on 6277. v2 uses MCP_INSPECTOR_API_TOKEN and one server on 6274.
2. Whether the current shell, the launch script, or a project .env sets MCP_INSPECTOR_API_TOKEN, MCP_PROXY_AUTH_TOKEN, or DANGEROUSLY_OMIT_AUTH. Names and set/unset only. A pinned MCP_INSPECTOR_API_TOKEN does not rotate. DANGEROUSLY_OMIT_AUTH=true disables the token.
3. How Inspector is started today: command, flags, catalog, config. Quote the launch banner with the token redacted. State whether the banner still prints a URL containing MCP_INSPECTOR_API_TOKEN.
4. If a process is already listening on 127.0.0.1:6274, record pid, command, and start time. Do not kill it. A bare http://127.0.0.1:6274 can still work: v2 injects window.__INSPECTOR_API_TOKEN__ into index.html and keeps a sessionStorage copy. The address bar staying clean is not proof the token was removed.
5. Fetch http://127.0.0.1:6274/ only if that process is the Inspector. Report whether the HTML contains the marker window.__INSPECTOR_API_TOKEN__ . Do not print the assigned value.
6. Do not open Inspector storage, keychain, or oauth files. Do not read phantom_cloud.py.

Write the report to /tmp/inspector_token_url_cause.md. Do not write under runs/. Reply: version, env names set, banner has token URL yes/no, listener pid, HTML marker present yes/no, one-sentence cause. Stop.
```
