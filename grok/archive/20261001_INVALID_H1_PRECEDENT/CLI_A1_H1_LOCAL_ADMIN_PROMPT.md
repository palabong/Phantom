PROJECT: phantom_cloud
UPDATED: 2026-09-28T21:45Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree (Drive phantom_cloud).
Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
Token → N/A. One human Chrome session on the device.

Task: open the researcher-owned admin tenant in local Chrome, then write a full prod_postdeploy archive in the same shape as the Fly smokes.

Allowlist after login:
- accounts.shopify.com
- partners.shopify.com
- admin.shopify.com
- admin.shopify.com/store/funk-it-up-sdzgxmea
Forbid: other merchants, Support chat, PCI, community, storefront password in files.

1. Open a normal device Chrome window (not Fly SSE).
2. Go to https://partners.shopify.com/ (not /login). Complete CF yourself if shown.
3. Sign in as palabong@wearehackerone.com. Do not write the password into chat, logs, SMOKE.md, protocol.json, or this prompt.
4. Open store funk it up → Admin.
5. Confirm the address bar is https://admin.shopify.com/store/funk-it-up-sdzgxmea (query string redacted). Staff list reachable = yes/no. Do not create staff.
6. Write archive on the device tree only:

   runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

   stamp = UTC now YYYYMMDDTHHMMSSZ
   mkdir must not overwrite an existing run dir.

   evaluate.json:
   {
     "source": "local-chrome",
     "server_url": null,
     "sessions": 1,
     "title": "<page title>",
     "href": "<origin+path, query redacted>",
     "host": "admin.shopify.com",
     "path": "/store/funk-it-up-sdzgxmea",
     "staffListReachable": true|false,
     "cf": false,
     "hasPassword": false
   }

   protocol.json:
   {
     "timestamp": "<stamp>",
     "target_url": "https://partners.shopify.com/",
     "server_url": null,
     "sessions": 1,
     "verdict": "PASS"|"FAIL",
     "reason": "local admin home"|"cf loop"|"wrong shop"|"other",
     "final_href": "<redacted href>",
     "results": [
       {"tool": "local-chrome partners", "status": "PASS"|"FAIL", "latency_ms": null, "details": "partners.shopify.com"},
       {"tool": "local-chrome admin", "status": "PASS"|"FAIL", "latency_ms": null, "details": "<final path>"}
     ]
   }

   SMOKE.md: same table layout as Fly smokes. Header fields: Target, Server (`local-chrome`), Sessions 1, Verdict, Reason, Final href.
   Lines: no password, no token, no email body, no screenshot of secrets.

7. Zip that folder. Reply: archive path, verdict, evaluate JSON, staffListReachable. Stop.

Pass: admin Home for funk-it-up-sdzgxmea + complete archive.
Fail: CF loop, other shop, or missing archive files.
Do not click Support. Do not open PCI. Do not run Fly tools in this task.
