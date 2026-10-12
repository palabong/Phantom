PROJECT: phantom_cloud
UPDATED: 2026-09-29T19:00Z
ENVIRONMENT: Official Grok Build 4.7 Medium — staff Chrome already logged in

CWD device tree. Staff only. No Fly. No deploy. No engine edits. Token → N/A.
Do not type passwords. Do not Publish. Do not Save theme. Do not edit Liquid.

H1-5 20260929T225522Z: /themes deniedUI=false, embed + editorManifest 200.
This run only measures impact on Themes (Sensitive class).

Land: https://admin.shopify.com/store/funk-it-up-sdzgxmea/themes
Allow: that path + online-store-web.shopifyapps.com embeds for this shop.
Forbid: settings, payments, other shops, Support, code save, publish.

1. Confirm staff tab, host admin.shopify.com, shop funk-it-up-sdzgxmea.
2. Open /themes. Record: theme cards visible? current theme name visible?
3. If a Customize / Personalizza / Edit code / Modifica codice control exists:
   record enabled true|false. Click Customize ONLY if present. Do not click Edit code.
4. If editor opens: record URL, whether sections/JSON are editable, whether Publish/Salva is enabled.
   Do not press Publish or Save.
5. Stop.

evaluate.json:
{
  "source": "local-chrome",
  "themesIndex": {"href":"","cardsVisible":true|false,"themeName":null},
  "customizeEnabled": true|false,
  "editorOpened": true|false,
  "editorHref": "",
  "saveEnabled": true|false,
  "publishEnabled": true|false,
  "impact": "none"|"view-index"|"open-editor"|"save-or-publish-enabled"
}

PASS if impact field is set.
impact save-or-publish-enabled or open-editor = keep as candidate.
impact none or view-index only = likely ineligible chrome; trail continues to settings after this archive.

Zip. Reply: path, verdict, evaluate JSON. Stop.
