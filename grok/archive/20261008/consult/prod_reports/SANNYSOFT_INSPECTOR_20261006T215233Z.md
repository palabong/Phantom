UPDATED: 2026-10-06T21:53Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# Sannysoft Inspector smoke — 20261006T215233Z

Source: operator Inspector exports attached this turn (protocol + network) plus the html AOM snapshot pasted in chat. Not a production-tree archive. Token path segment omitted. L1 not stamped (green light required). Production tree not modified. Machine version not present in the export; do not treat this as a version-166 proof or as a redeploy proof.

## Transport

- Host: `https://phantom-cloud-engine.fly.dev` (fra, `fly-request-id` `*-fra`, server `Fly/6d530f8f2`).
- SSE `GET /sse/?token=[REDACTED]` → 200 `text/event-stream`, `cache-control: no-store`, `x-accel-buffering: no`. Stream export `eventCount` 7.
- Messages `POST /messages/t/[REDACTED]?session_id=fbf86f1eb5bd4698b941abd7c2bcf530` → 202 `Accepted` on every call.
- Inspector client `mcp-inspector` 2.9.0 offered protocol `2025-11-25`. Server negotiated `2024-11-05`. `serverInfo` Phantom-Cloud 1.0.0. Capabilities: `tools.listChanged=false`, `experimental={}`. No prompts/resources capability advertised.

## Protocol matrix

| Call | Result | Duration |
|---|---|---|
| initialize | ok, protocol 2024-11-05 | 152 ms |
| notifications/initialized | sent | — |
| tools/list | 6 tools: navigate, get_snapshot, click, type, evaluate, wait | 109 ms |
| prompts/list | -32601 Method not found | 377 ms |
| resources/list | -32601 Method not found | 419 ms |
| navigate `https://bot.sannysoft.com/` | isError false, "Navigazione completata" | 20558 ms |
| get_snapshot `{}` (html default) | isError false, AOM snapshot | 272 ms |

`prompts/list` and `resources/list` are Inspector probes, not engine defects. The server does not advertise those capabilities.

This is not the 6-tool acceptance in `CLI_SANNYSOFT_SMOKE_PROMPT.md`. Missing: `wait`, `get_snapshot mode=ax`, `evaluate`, `type` N/A check, `click` on a live ref, `click` miss selector. Do not file it as a `runs/prod_postdeploy_*` PASS.

## Stealth (page-labelled only)

Intoli rows present in the distilled snapshot: WebDriver missing (passed), WebDriver Advanced passed, Chrome present (passed), Permissions prompt, Plugins Length 5, PluginArray passed, Languages `en-US,en`. Broken image 16x16. No `HeadlessChrome` in the UA.

Fingerprint-scanner blocks in the snapshot are all labelled `ok`: PHANTOM_UA, PHANTOM_PROPERTIES, PHANTOM_ETSL (33), PHANTOM_LANGUAGE, PHANTOM_WEBSOCKET, MQ_SCREEN, PHANTOM_OVERFLOW, PHANTOM_WINDOW_HEIGHT, HEADCHR_UA, HEADCHR_CHROME_OBJ, HEADCHR_PERMISSIONS, HEADCHR_PLUGINS, HEADCHR_IFRAME, CHR_DEBUG_TOOLS, SELENIUM_DRIVER, CHR_BATTERY, CHR_MEMORY, TRANSPARENT_PIXEL, SEQUENTUM, VIDEO_CODECS (`h264` probably). `webDriver` false. Selenium/phantom attribute arrays all false.

UA: `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36`. L0 lock 2026-10-01 is Chrome 154.0.8037.92 on machine version 166. This export does not carry the binary version. Major 155 in `navigator.userAgent` is a delta versus that lock and versus the 2026-09-23 eval (`Chrome/153.0.0.0`). Not enough to claim a redeploy.

WebGL vendor `Google Inc. (NVIDIA)`, renderer `ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)`. Matches `STEALTH_INJECTION_PAYLOAD` as documented in L2-arch and the 2026-09-23 eval. The D3D11/RTX string on a Linux UA is the designed spoof, not a new miss. SwiftShader is not claimed solved.

Canvas1–5 hash identical: `-419353324`. Consistent with deterministic canvas noise; not an independent entropy sample. `deviceMemory` 8. Battery charging true, level 1. Plugins are the five internal PDF viewers. `multimediaDevices` speakers/micros/webcams 0. Window outer 1919x1079, screen 1920x1080, `wScreenX` 10. `detailChrome.webstore` / `runtime` report a constructor TypeError; the page still labels HEADCHR_CHROME_OBJ ok.

Snapshot distillation emitted one ref only: `[e1: A 'unnamed']`. Enough to prove AOM refs, not enough for a click acceptance.

## Verdict

Transport and the two exercised tools passed on the Fly SSE. Intoli and fingerprint-scanner labels in this html snapshot match the prior production stealth shape, including the RTX 3080 WebGL spoof. Not a 6-tool smoke. Not a Shopify finding. Not a draft.
