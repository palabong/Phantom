UPDATED: 2026-10-01T12:24Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# Agent process diagram

Session agent only. Not the device CLI. Not a production deploy.

```mermaid
flowchart TD
  U[User turn] --> L0[L0 grok/AGENTS.md]
  L0 --> L1[L1 project_memory]
  L1 --> L2[L2 README read-only]
  L2 --> L2A[L2-arch phantom_cloud_architecture.md]
  L2A --> SCOPE{Consult scope}
  SCOPE --> G[.grok/]
  SCOPE --> P[phantom_cloud/ read-only]
  SCOPE --> STOP[Outside scope: stop]
  G --> OBJ[Objective lock: lead-evaluation]
  P --> EV[L3 SMOKE + 20260924 six-tool run]
  EV --> ST[L4 stealth eval caveats]
  ST --> COM[L5 commercial headlines]
  OBJ --> FREEZE[Engine freeze: no phantom_cloud.py / Dockerfile / fly.toml / requirements.txt]
  FREEZE --> VEC[Open vectors: H1 RoE / invitational / API-MCP / managed / pilot]
  VEC --> OUT[Italian answer or English CLI prompt]
  OUT --> WAIT[Wait. No inferred cleanup]
```

Branch split:

- This session writes only under `grok/` unless the same turn names a path.
- Device Grok Build 4.7 on Drive `1msmuBIu_28tNkjBxhKQ6S-x9DzfZjpO5` is the operative CLI. It does not load this L0 stack.
- Fly `phantom-cloud-engine` / `fra` / `https://phantom-cloud-engine.fly.dev` is the production machine. This diagram does not deploy it.

Tool surface: `navigate`, `get_snapshot` (html|ax), `click`, `type`, `evaluate`, `wait`.

Accepted smoke: `runs/prod_postdeploy_20260924T153949Z`. SwiftShader is not solved.
