UPDATED: 2026-10-07T12:10Z
VERSION: fly-193-operator / git-6e95b31 / ingest-2026-10-01T12:58Z
PROJECT: phantom_cloud

# H1 Shopify — roadmap operativo

Canale: CLI in `/Users/daniele_palagi/Desktop/phantom_cloud 2` → Inspector già su `http://127.0.0.1:6274` → SSE `https://phantom-cloud-engine.fly.dev`. Una sessione. Sei tool. Nessun edit al production tree. Nessun deploy in una slice bounty.

L0 resta `fly-166` / ingest `2026-10-01T12:58Z`. Il terminale operatore del 2026-10-07 dice machine `78197e2be34d78` version 193, health online. Non è stato riletto `fly status` da questo agente. Il warmup Sannysoft dello stesso giorno non è evidenza di ticket e non è la baseline a sei tool (`runs/prod_postdeploy_20260924T153949Z`).

Secret del paste (Unkey, token Inspector) non sono in questo file.

## Cosa conta come ticket

Solo tenant creati con `palabong@wearehackerone.com`. Handle `palabong`. Niente Support. Niente altri merchant. Niente PII acquirente in `runs/`.

- A: `funk-it-up-sdzgxmea.myshopify.com` (Grow / App Development, Bogus Gateway, theme `test-data`).
- B: `xxxxxx-r48zg9i1.myshopify.com` solo se creato da questo handle.
- Classi che valgono: lettura/scrittura staff di Settings, Payments, Themes, Orders o PII senza quel grant; UI deny + API/GraphQL 200 sulla stessa risorsa; IDOR cross-shop sull'oggetto `10323603947706` (o equivalente); prezzo, stock o stato di pubblicazione che contraddice l'admin e muove denaro.
- Non vale da solo: prezzo pubblico su title test-data hidden/archived (H1-1c / H1-6f). Add to cart non è stato inviato.

## Chiuso, non citare

- `archive/20261001_INVALID_H1_PRECEDENT/` — Chrome locale / AppleScript. Non evidenza.
- Note H1-0 … H1-1f su `:8000`. Non source of truth.
- H1-1g `20261001T131829Z`: Cloudflare su `accounts.shopify.com/login`. Nessun click. Non è un finding. Non ritentare alla cieca. Non cliccare il challenge.
- H1-6d: la stringa gate del 28 settembre rifiutata. Password di sostituzione solo same-turn, mai in L1.
- H1-6f `20261001T140453Z`: hidden `$749.95`, archived `$629.95`, cart non inviato, stock è un miss di regex. Non è una bozza.

## Punto di ripresa

H1-6h non eseguito. Ultimo run `20261007T000956Z` GATE: `/products/the-hidden-snowboard` è finito su `/password`. Ref di quel gate: `e1` authenticity_token, `e2` password, `e3` Enter, `e4` Log in here. Il type precedente su `e1` è l'errore da non ripetere. L'unlock `20261001T135742Z` non è questa sessione.

Regola click: ref `eN` dello snapshot html immediatamente precedente. Uno snapshot `ax` sostituisce la mappa. `e1` dopo `ax` è ERROR.

## Ordine

1. H1-6h — sblocco storefront. `type` solo su `e2`, click solo `e3` dello snapshot html appena preso. Password solo nell'argomento MCP di questo turno. Se resta `/password`: GATE-STUCK e stop.
2. H1-6i — stock vero sui due URL, stessa sessione sbloccata. Nessun cart, nessun admin, nessun `e4`.
   - `https://funk-it-up-sdzgxmea.myshopify.com/products/the-hidden-snowboard`
   - `https://funk-it-up-sdzgxmea.myshopify.com/products/the-archived-snowboard`
   Lettura: `available`, variant id, prezzo, stato publish se è nel DOM. Il flag regex di H1-6f non si riusa.
3. Chiusura classe storefront. Se prezzo/stock pubblici non contraddicono l'admin e non muovono denaro: classe chiusa, non bozza. Se contraddicono: fermarsi e scrivere la bozza da `evaluate`, non da memoria.
4. H1-2 — solo con secret staff nello stesso turno. Leggere prodotto `10323603521722` sul grant di A. Non Save. Se Cloudflare: stop, nessun click.
5. H1-5 — sulla stessa sessione staff, UI deny contro XHR/GraphQL della stessa risorsa. Uno alla volta.
6. H1-7 — store B solo se questo handle l'ha creato. Contesto B che mostra l'oggetto di A. Staff isolato, non membro di A.

Fatto quando esiste una bozza submit-ready in `grok/`, oppure una classe nominata è chiusa con evidenza MCP di produzione.

## Vincoli di ogni prompt CLI

Inglese. CWD `/Users/daniele_palagi/Desktop/phantom_cloud 2`. Tool MCP soltanto. Vietato: client Python, `smoke_test.py`, `execute_task.py`, osascript, cliclick, `page.fill`, secondo Inspector, fly deploy, edit engine, Support, checkout, signup, `accounts` finché la slice non è H1-2. Non stampare password o token. Archive sotto `runs/prod_postdeploy_<UTC>/` sul device, non in questo albero se non nominato.
