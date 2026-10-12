UPDATED: 2026-09-29T19:52Z
PROJECT: phantom_cloud
SOURCE: attachment prod_postdeploy_20260929T113135Z.zip (user-authorized this turn)
ENGINE FREEZE: stands
BASELINE UNCHANGED: runs/prod_postdeploy_20260924T153949Z

# Validity of prod_postdeploy_20260929T113135Z

## Archive integrity

- Zip contains run dir + AppleDouble `__MACOSX` sidecars. Payload files: SMOKE.md, protocol.json, html_snapshot.txt, ax_snapshot.txt, evaluate.json.
- Internal consistency: SMOKE, protocol, evaluate.json, and snapshots agree on host, title, href `/`, hasPasswordForm false.
- No live token in protocol (unlike 20260924 which had a masked fly.dev SSE URL). No password string.
- Not copied into runs/.

## Compared with known runs

| run | target | type | click hit | click miss scored | gate | role |
|-----|--------|------|-----------|-------------------|------|------|
| 20260924T153949Z (accepted 6-tool) | vercel test-nextjs | PASS | PASS | PASS (controlled) | n/a | commercial/engine baseline |
| 20260928T164449Z (A1 smoke note) | shopify own /password | N/A | PASS ax14 Enter | PASS | password true | allowlist evidence |
| 20260928T180941Z (A1 unlock note) | shopify own / | PASS e2 | PASS e3 Enter | not in that matrix | unlocked | storefront unlock |
| 20260929T113135Z (this zip) | shopify own / | absent | N/A fail 0ms | table FAIL / text controlled | unlocked | storefront re-probe |

## Verdict on claimed PASS

PASS is valid only as a **storefront reachability + snapshot + evaluate** probe on the already-unlocked A1 shop.

It is **not** a valid replacement for the 20260924 six-tool acceptance:

- `type` never invoked.
- `click ref` empty request, duration 0, note "click N/A".
- SMOKE scores `click miss` as fail even though response is the same controlled miss used as PASS since 20260924 (~10.3s, `#phantom-missing-target`).
- Reason text "Successfully ran all tools" is false: 6 tools listed, 4 exercised (list, navigate, wait, snapshots, evaluate); type omitted; click not hit.

## Page state vs prior A1

- href `https://funk-it-up-sdzgxmea.myshopify.com/` and hasPasswordForm false — same unlocked state as 20260928T180941Z, not the /password gate of 164449Z.
- Richer snapshots than password page (html ~3.9 KiB vs 286 B; ax ~15.7 KiB vs 918 B): cookie banner, cart empty, featured products, Search, Catalog, Contact, FAQ, About, Log in.
- Cookie ALERTDIALOG is first AX content; click N/A is consistent with runner not selecting a ref (not a navigation failure).
- Navigate 4743 ms aligns with unlock (5154 ms) and 20260924 (4709 ms), not the 24 s cold first smoke.

## Not claimed

- New commercial baseline.
- Full 6-tool matrix.
- SwiftShader solved.
- Admin / checkout / typed catalog search.
- Proof the probe hit Fly vs a local MCP (no server_url in this protocol).
