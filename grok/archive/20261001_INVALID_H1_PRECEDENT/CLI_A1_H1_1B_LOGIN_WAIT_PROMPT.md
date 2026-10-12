PROJECT: phantom_cloud
UPDATED: 2026-09-28T21:06Z
VERSION: fly-163 / git-6e95b31 / ingest-2026-09-28T14:35Z

CWD device production tree. Inspector on https://phantom-cloud-engine.fly.dev
Do not restart/deploy/edit engine. Token → [REDACTED]. One session.

Task H1-1b: wait out Turnstile / fix partners path. Do not type. Do not submit credentials.

Allowlist hosts:
- accounts.shopify.com
- partners.shopify.com
- admin.shopify.com
Forbid: *.myshopify.com, Support, community, academy, cdn, PCI.

Hard stop if about:blank or host outside the three.
Do not persist emails/phones/tokens/passwords.

EVAL:
JSON.stringify({title:document.title,href:location.href,host:location.hostname,path:location.pathname,ready:document.readyState,hasPassword:!!document.querySelector('input[type=password]'),hasEmail:!!document.querySelector('input[type=email],input[name=email],input[name=account_email]'),cf: /just a moment|turnstile|cf-turnstile/i.test(document.title+' '+document.body.innerText.slice(0,200))})

1. tools/list
2. navigate https://accounts.shopify.com/
3. wait {"delay_ms":8000}
4. evaluate EVAL
5. get_snapshot html
6. If still cf/just-a-moment and no email: wait {"delay_ms":8000} → evaluate EVAL again → snapshot html
7. navigate https://partners.shopify.com/
8. wait {"delay_ms":3000}
9. evaluate EVAL + get_snapshot html
10. navigate https://admin.shopify.com/
11. wait {"delay_ms":8000}
12. evaluate EVAL + get_snapshot html
13. Stop. No type. No click.

Pass: three hosts stay in allow set (admin may land on accounts.shopify.com/session-service/*).
Report whether hasEmail/hasPassword became true. That flag decides H1-2, not this run.

Archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,html_snapshot.txt,evaluate.json}
Reply: path, matrix, all evaluate JSON. Stop.
