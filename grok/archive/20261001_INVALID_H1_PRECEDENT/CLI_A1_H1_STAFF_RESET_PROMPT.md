PROJECT: phantom_cloud
UPDATED: 2026-09-29T21:55Z
ENVIRONMENT: Official Grok Build 4.7 Medium — operator + optional local Chrome
CWD device production tree.

Do not use https://phantom-cloud-engine.fly.dev.
Do not start phantom_cloud.py. Do not fly deploy. Do not edit engine files.
Token → N/A.

Do NOT type any password. Do NOT solve hCaptcha. Do NOT brute-force.
Do NOT persist mailbox contents, reset links, or the new password in runs/ or chat.

Fact: palabong+staff@wearehackerone.com shows “Password errata”. Invite was resent. Row is still In attesa.

Task: human password reset for that alias, then accept the new invite. Agent only records URLs and verdict.

1. Human, staff Chrome profile (not owner):
   a. On the Accedi page click Password dimenticata?
   b. Request reset for palabong+staff@wearehackerone.com only.
   c. Complete hCaptcha yourself if shown.
   d. Open that mailbox (same wearehackerone alias). Use the official Shopify reset mail only.
   e. Set a new password. Store it in your password manager, not in this prompt.
   f. Sign in as palabong+staff@wearehackerone.com.
   g. Open the NEW invite from the owner. Finish join on funk-it-up-sdzgxmea only.
2. Human, owner profile: refresh
   https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings/organization-account
   Confirm the staff row is Attivo. Permissions still Prodotti Visualizza only. Do not add grants.
3. Agent writes archive runs/prod_postdeploy_<UTC>/{SMOKE.md,protocol.json,evaluate.json}

evaluate.json:
{
  "source": "local-chrome",
  "staffLogin": "reset-then-signin"|"failed",
  "inviteAccepted": true|false,
  "rowStatus": "Attivo"|"In attesa"|null,
  "grantedStillProductsViewOnly": true|false
}

PASS only if rowStatus is Attivo.
FAIL if still In attesa or captcha/reset not completed by the human.

Reply: path, verdict, evaluate JSON. No passwords. Stop.
