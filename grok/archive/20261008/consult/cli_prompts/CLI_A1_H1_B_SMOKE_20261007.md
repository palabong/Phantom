UPDATED: 2026-10-07T18:50Z
VERSION: fly-193 / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# H1 restart — store B smoke

```
H1 restart on store B. Same Inspector session. Do not type. Do not click. Do not deploy. Do not touch store A.

Host only: xxxxxx-r48zg9i1.myshopify.com
HARD STOP: about:blank, another host, Support, accounts.shopify.com, admin.shopify.com, /checkout, /signup, Cloudflare. If path is /password, verdict GATE and stop.

1. tools/list
2. navigate {"url":"https://xxxxxx-r48zg9i1.myshopify.com/"}
3. wait {"delay_ms":1500}
4. get_snapshot {"mode":"html"}
5. evaluate {"expression":"JSON.stringify({title:document.title,href:location.href,path:location.pathname,hasPasswordForm:!!document.querySelector('input[type=password],input[name=password]'),nProduct:document.querySelectorAll('a[href*=\"/products/\"]').length})"}

Archive: runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Reply: final href, hasPasswordForm, title, verdict. Stop.
```
