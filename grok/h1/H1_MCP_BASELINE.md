UPDATED: 2026-10-01T00:25Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z
PROJECT: phantom_cloud

# H1 trail — MCP baseline only

Channel (mandatory, state this path in every prompt and every reply): CLI operator → MCP Inspector already running → existing SSE http://127.0.0.1:8000/sse/?token=<Inspector> → Phantom local engine → six tool calls only (tools/list, navigate, get_snapshot, click, type, evaluate, wait). Not desktop Chrome.

Tools only: navigate, get_snapshot (html|ax), click, type, evaluate, wait.
Click: {"ref":"eN"|"axN"} from the snapshot taken immediately before. Never CSS "a, button".
type: only when the same-turn prompt supplies the secret. H1-0 supplies none.
MAX_CONCURRENT_SESSIONS = 1. Do not open a second Inspector or a second SSE.

Stealth is a navigation property. Do not claim SwiftShader solved. Do not click Turnstile / hCaptcha.

Tenant (researcher-owned only):
- A: funk-it-up-sdzgxmea.myshopify.com
- B: xxxxxx-r48zg9i1.myshopify.com
Admin hosts stay in later phases: admin.shopify.com, accounts.shopify.com, partners.shopify.com.

Order:
- H1-0 — PASS-engine 20260930T233136Z (inspector+local :8000). Landed /password. Note A1_H1_0_NOTE_20260930T233136Z.md
- H1-0b — PASS-engine 20261001T001432Z. Unlocked. /collections/all, 17 OOS, webdriver false. Note A1_H1_0B_NOTE_20261001T001432Z.md
- H1-1d rewind 2026-10-01T11:59Z. Login host is admin.shopify.com, not accounts. Prompt CLI_A1_H1_1D_ADMIN_STATUS_PROMPT.md. accounts passkey run is not the login path.

Precedent H1-1…H1-8 notes/prompts: grok/archive/20261001_INVALID_H1_PRECEDENT/ (INVALID-CRAP).

Done when: submit-ready draft in grok/ produced from MCP evaluate.json, or a named class exhausted with MCP evidence.
