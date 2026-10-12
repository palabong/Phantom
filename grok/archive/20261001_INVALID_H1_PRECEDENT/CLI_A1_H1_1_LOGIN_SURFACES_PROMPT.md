PROJECT: phantom_cloud
UPDATED: 2026-09-28T20:45Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Inspector on https://phantom-cloud-engine.fly.dev
Do not restart/deploy/edit engine. Token → [REDACTED]. One session.

Task H1-1: map Shopify login surfaces for the next authenticated run. Do not type. Do not submit.

Allowlist hosts only:
- https://accounts.shopify.com/
- https://partners.shopify.com/
- https://partners.shopify.com/login
- https://admin.shopify.com/
(redirects between these three hosts are allowed)
Forbid: any *.myshopify.com, Support, community, academy, cdn, PCI, other shops.

Hard stop if about:blank OR host not in {accounts.shopify.com, partners.shopify.com, admin.shopify.com}.
Do not persist emails/phones/tokens/passwords.

1. tools/list
2. navigate https://accounts.shopify.com/
3. wait 800
4. evaluate JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,ready:document.readyState,hasPassword:!!document.querySelector('input[type=password]'),hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account_email]')})
5. get_snapshot html
6. navigate https://partners.shopify.com/login
7. wait 800
8. same evaluate + get_snapshot html
9. navigate https://admin.shopify.com/
10. wait 800
11. same evaluate + get_snapshot html
12. Stop. No type. No click except what navigate itself follows. No storefront.

Pass: three evaluates, each host in the allow set.
Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Reply: path, matrix, three evaluate JSON. Stop.
