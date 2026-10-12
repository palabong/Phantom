UPDATED: 2026-10-06T23:44Z
VERSION: fly-166 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# Evaluation — prod_postdeploy_20261006T234158Z

Source: artifacts/prod_postdeploy_20261006T234158Z. Not under phantom_cloud/runs/. Token not present. Not a 6-tool acceptance.

Target https://bot.sannysoft.com/. Machine 78197e2be34d78 version 192. Image phantom-cloud-engine:deployment-01M49M4AM14QB0SMXE3624KX25.

| Step | Result |
|---|---|
| tools/list | PASS, six tools |
| navigate | PASS |
| wait 500ms | PASS |
| get_snapshot html | PASS, 14829 bytes, one ref [e1: A 'unnamed'] |
| get_snapshot ax | PASS, 59531 bytes, zero refs |
| evaluate | PASS, title Antibot, href bot.sannysoft.com, UA Chrome/155.0.0.0 |
| type | N/A, no input |
| click ref e1 | FAIL. Engine text: ref e1 not found, run get_snapshot. Archive also says isError false |
| click_miss | PASS on the controlled missing-selector text. Archive also says isError false |

Html snapshot labels: WebDriver missing passed, WebDriver Advanced passed, Chrome present, Permissions prompt, Plugins 5 PluginArray passed. Same click failure mode as runs/prod_postdeploy_20260925T190747Z: e1 was taken from the html snapshot, then ax ran, then click used the stale ref. No latency column. No network.json.
