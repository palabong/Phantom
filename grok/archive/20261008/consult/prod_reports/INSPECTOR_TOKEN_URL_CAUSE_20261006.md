UPDATED: 2026-10-06T22:52Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# Inspector session-token URL — cause from operator report

Source: operator paste of the investigation, checked 2026-10-06 against the process already listening on 127.0.0.1:6274. No second Inspector started. Catalog not opened. Token values not stored.

- Binary: not on PATH. Live process `node …/.npm/_npx/5a9d879542beca3a/node_modules/.bin/mcp-inspector`, package 2.9.0. Node v24.18.0. npm 11.16.0. No 6277 in that package. Auth env name `MCP_INSPECTOR_API_TOKEN`. Legacy `MCP_PROXY_AUTH_TOKEN` read only if the new name is unset.
- Env: `MCP_INSPECTOR_API_TOKEN`, `MCP_PROXY_AUTH_TOKEN`, `DANGEROUSLY_OMIT_AUTH` unset in the shell, in pid 85183, and in parent 85161. Absent from checkout `.env` and `.env.example`. No launch script in the checkout. Token is generated with `randomBytes(32)` when auth token is empty and omit-auth is false.
- Start: `npm exec @modelcontextprotocol/inspector --web --config /Users/daniele_palagi/.mcp-inspector/mcp.json`. Child pid 85183, parent 85161, parent of that is 1. Started Mar 6 Ott 23:25:19 2026. cwd `/Users/daniele_palagi/.grok/worktrees/desktop-phantom-cloud-2/2026-10-06-93fbe1ab`. stdout/stderr `/private/tmp/phantom-inspector.log`. stdin `/dev/null`.
- Banner in that log still prints `http://127.0.0.1:6274?MCP_INSPECTOR_API_TOKEN=[REDACTED]` and a separate auth-token line. `printServerBanner` builds the query unless omit-auth or empty token.
- `GET /` → 200 `text/html`, 897 bytes, title MCP Inspector. Marker `window.__INSPECTOR_API_TOKEN__` present. HTML does not contain the string `MCP_INSPECTOR_API_TOKEN`. Client copies the global into `sessionStorage` under that key, and reads the query string only if the global is missing. `history.replaceState(..., "/")` in this bundle runs on `/oauth/callback`, not on first load of `/`.

Cause stated by the report: the launch banner still includes the token query. A bare `http://127.0.0.1:6274` still authenticates because 2.9.0 injects the global into `index.html` and the page copies it into `sessionStorage`. The address bar does not have to keep the query.
