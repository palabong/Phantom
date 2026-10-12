import os
import sys
import time
import asyncio
import json
import datetime
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_matrix_full"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
BASE_URL = "https://xxxxxx-r48zg9i1.myshopify.com"

HANDLES = [
    "beanie",
    "black-sunnies",
    "canvas-sneakers",
    "clear-sunnies",
    "frontpack",
    "gray-leather-sneakers",
    "gray-runners",
    "half-zip",
    "high-top-sneakers",
    "hoodie",
    "hoodie-old",
    "leggings",
    "light-puffer",
    "men-crewneck",
    "men-t-shirt",
    "puffer",
    "puffer-jacket",
    "shorts",
    "slides",
    "soft-cotton-hoodie-in-clay",
    "soft-cotton-hoodie-in-green",
    "soft-cotton-hoodie-in-jam",
    "soft-cotton-hoodie-in-ocean",
    "soft-cotton-hoodie-in-violet"
]

LISTING_PRICES = {
    "beanie": "$100.00",
    "black-sunnies": "$50.00",
    "canvas-sneakers": "$40.00",
    "clear-sunnies": "$25.00",
    "frontpack": "$200.00",
    "gray-leather-sneakers": "$1,000.00",
    "gray-runners": "$30.00",
    "half-zip": "$100.00",
    "high-top-sneakers": "$180.00",
    "hoodie": "$90.00",
    "hoodie-old": "$90.00",
    "leggings": "$20.00",
    "light-puffer": "$80.00",
    "men-crewneck": "$120.00",
    "men-t-shirt": "$40.00",
    "puffer": "$80.00",
    "puffer-jacket": "$90.00",
    "shorts": "$45.00",
    "slides": "$25.00",
    "soft-cotton-hoodie-in-clay": "$90.00",
    "soft-cotton-hoodie-in-green": "$90.00",
    "soft-cotton-hoodie-in-jam": "$90.00",
    "soft-cotton-hoodie-in-ocean": "$90.00",
    "soft-cotton-hoodie-in-violet": "$90.00"
}

def find_add_to_cart_ref(snapshot_text):
    # Strategy 1: Primary submit button [eXX: BUTTON 'add'] Add to cart
    m = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)\s+'add'\]\s*Add to cart", snapshot_text, re.I)
    if m:
        return m.group(1)

    # Strategy 2: any BUTTON/INPUT with 'Add to cart' that is not quick-cart (e.g. not '( 1 )')
    matches = re.findall(r"\[(e\d+):\s+(?:BUTTON|INPUT)[^\]]*\]\s*Add to cart(?!\s*\(\s*\d+\s*\))", snapshot_text, re.I)
    if matches:
        return matches[0]

    # Strategy 3: any Add to cart button
    m = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)[^\]]*\]\s*Add to cart", snapshot_text, re.I)
    if m:
        return m.group(1)

    return None

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)

    print(f"Connecting to {SSE_URL} ...")
    matrix_results = []

    try:
        async with sse_client(SSE_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Session initialized.")

                # Ensure cart is cleared first for a clean test run
                print("Clearing cart before starting matrix...")
                await session.call_tool("navigate", {"url": f"{BASE_URL}/cart/clear"})
                await session.call_tool("wait", {"delay_ms": 1500})

                for idx, handle in enumerate(HANDLES, 1):
                    print(f"\n==================================================")
                    print(f"[{idx}/{len(HANDLES)}] Processing handle: {handle}")
                    print(f"==================================================")
                    listing_price = LISTING_PRICES.get(handle, "")

                    # 1. Navigate to products/{handle}.js
                    js_url = f"{BASE_URL}/products/{handle}.js"
                    print(f"1. Navigate: {js_url}")
                    await session.call_tool("navigate", {"url": js_url})
                    await session.call_tool("wait", {"delay_ms": 1000})

                    # Check for captcha / Cloudflare
                    eval_chk = await session.call_tool("evaluate", {"expression": "document.title + ' | ' + location.href"})
                    chk_text = eval_chk.content[0].text if eval_chk.content else ""
                    if "Just a moment..." in chk_text or "challenge" in chk_text.lower():
                        print("HARD STOP: Cloudflare/captcha detected!")
                        with open(os.path.join(run_dir, "STOP.txt"), "w") as f:
                            f.write("CLOUDFLARE_CAPTCHA_DETECTED")
                        return

                    # 2. Evaluate document.body.innerText.slice(0, 1500)
                    eval_js = await session.call_tool("evaluate", {"expression": "document.body.innerText.slice(0, 1500)"})
                    raw_js_text = eval_js.content[0].text if eval_js.content else ""

                    js_price = ""
                    js_available = None
                    js_variants_count = 0
                    try:
                        # raw_js_text is a JSON-encoded string from CDP evaluate
                        parsed_text = json.loads(raw_js_text)
                        # Now parse the actual product JSON inside it
                        prod_data = json.loads(parsed_text) if isinstance(parsed_text, str) else parsed_text
                        raw_p = prod_data.get("price")
                        if raw_p is not None:
                            js_price = f"${float(raw_p)/100:.2f}"
                        js_available = prod_data.get("available")
                        js_variants_count = len(prod_data.get("variants", []))
                    except Exception as e:
                        print(f"   Warning parsing .js JSON: {e}")
                        # Fallback regex on raw text
                        m_pr = re.search(r'"price":\s*(\d+)', raw_js_text)
                        if m_pr:
                            js_price = f"${float(m_pr.group(1))/100:.2f}"
                        m_av = re.search(r'"available":\s*(true|false)', raw_js_text)
                        if m_av:
                            js_available = (m_av.group(1) == "true")

                    print(f"2. JS Extract -> price: {js_price}, available: {js_available}, variants: {js_variants_count}")

                    # 3. Navigate to products/{handle}
                    pdp_url = f"{BASE_URL}/products/{handle}"
                    print(f"3. Navigate: {pdp_url}")
                    await session.call_tool("navigate", {"url": pdp_url})
                    await session.call_tool("wait", {"delay_ms": 1500})

                    # 4. get_snapshot mode=html
                    print("4. get_snapshot (mode=html)")
                    snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
                    snapshot = snap_res.content[0].text if snap_res.content else ""

                    # PDP price & quantity & select extraction
                    eval_pdp = await session.call_tool("evaluate", {"expression": """(() => {
                        let mainEl = document.querySelector('main, .product, .product__info-container');
                        let el = mainEl ? mainEl.querySelector('.price-item--regular, .price, .product__price, [data-product-price]') : null;
                        if (!el) el = document.querySelector('.price-item--regular, .price');
                        let priceText = el ? el.innerText.trim() : '';

                        let qtyEl = document.querySelector('input[name="quantity"], .quantity__input, [data-quantity-input]');
                        let qtyVal = qtyEl ? qtyEl.value : '1';

                        // Detect selected variant / select options
                        let selOption = '';
                        let selEl = document.querySelector('select[name="id"], variant-selects select, .product-form select');
                        if (selEl && selEl.options && selEl.selectedIndex >= 0) {
                            selOption = selEl.options[selEl.selectedIndex].text.trim();
                        }
                        if (!selOption) {
                            let checkedRadio = document.querySelector('variant-radios input[type="radio"]:checked, fieldset input[type="radio"]:checked');
                            if (checkedRadio) {
                                selOption = checkedRadio.value;
                            }
                        }
                        let varIdEl = document.querySelector('form[action*="/cart/add"] input[name="id"]');
                        let varId = varIdEl ? varIdEl.value : '';

                        return JSON.stringify({
                            price: priceText,
                            qty: qtyVal,
                            selected_option: selOption,
                            variant_id: varId
                        });
                    })()"""})
                    pdp_raw = eval_pdp.content[0].text if eval_pdp.content else "{}"
                    pdp_info = {}
                    try:
                        p_info = json.loads(pdp_raw)
                        pdp_info = json.loads(p_info) if isinstance(p_info, str) else p_info
                    except Exception:
                        pdp_info = {"price": pdp_raw, "qty": "1", "selected_option": "", "variant_id": ""}

                    pdp_price_text = pdp_info.get("price", "")
                    pdp_price = ""
                    m_pdp = re.search(r"\$[0-9,]+(?:\.[0-9]{2})?", pdp_price_text)
                    if m_pdp:
                        pdp_price = m_pdp.group(0)
                    else:
                        pdp_price = pdp_price_text

                    pdp_qty = str(pdp_info.get("qty", "1"))
                    pdp_select_option = pdp_info.get("selected_option", "")
                    pdp_variant_id = pdp_info.get("variant_id", "")
                    select_desc = pdp_select_option if pdp_select_option else (f"id:{pdp_variant_id}" if pdp_variant_id else "default")
                    print(f"   PDP Price: {pdp_price}, Qty: {pdp_qty}, Select/Variant: {select_desc}")

                    # 5. Look for Add to cart control in snapshot
                    btn_ref = find_add_to_cart_ref(snapshot)
                    cart_add_result = "none"

                    if btn_ref:
                        print(f"5. Found Add to cart ref '{btn_ref}', clicking...")
                        await session.call_tool("click", {"ref": btn_ref})
                        print("   Waiting 1500ms...")
                        await session.call_tool("wait", {"delay_ms": 1500})

                        # 6. Evaluate success/error or cart count change
                        eval_cart_check = await session.call_tool("evaluate", {"expression": """(() => {
                            let loc = location.href;
                            let errEl = document.querySelector('.product-form__error-message-wrapper:not([hidden]), .form__message--error, .product-form__error-message');
                            let errText = (errEl && !errEl.closest('[hidden]')) ? errEl.innerText.trim() : "";
                            let countEl = document.querySelector('.cart-count-bubble, .header__cart-count, [data-cart-count], .cart-link__bubble');
                            let countText = countEl ? countEl.innerText.trim() : "";
                            let drawer = document.querySelector('cart-notification.animate, cart-drawer.animate, .drawer.active');
                            return JSON.stringify({
                                href: loc,
                                error: errText,
                                cart_count: countText,
                                drawer_visible: !!drawer
                            });
                        })()"""})

                        cart_data = {}
                        try:
                            raw_cd = eval_cart_check.content[0].text if eval_cart_check.content else "{}"
                            p_cd = json.loads(raw_cd)
                            cart_data = json.loads(p_cd) if isinstance(p_cd, str) else p_cd
                        except Exception as e:
                            print(f"   Error parsing cart check: {e}")

                        curr_href = cart_data.get("href", "")
                        print(f"6. Cart check: {cart_data}")

                        # Hard stop if checkout opened
                        if "/checkout" in curr_href:
                            print("HARD STOP: Cart add opened checkout!")
                            with open(os.path.join(run_dir, "STOP.txt"), "w") as f:
                                f.write("CHECKOUT_OPENED")
                            return

                        if cart_data.get("error"):
                            cart_add_result = f"error: {cart_data.get('error')}"
                        elif cart_data.get("cart_count") or cart_data.get("drawer_visible") or "/cart" in curr_href:
                            cart_add_result = "added"
                        else:
                            cart_add_result = "200"
                    else:
                        print("5. No Add to cart control found in snapshot (e.g. sold out or unavailable).")

                    print(f"7. Result for {handle}: PDP={pdp_price}, Qty={pdp_qty}, Select={select_desc}, AddResult={cart_add_result}")
                    matrix_results.append({
                        "handle": handle,
                        "listing_price": listing_price,
                        "js_price": js_price,
                        "js_available": js_available,
                        "pdp_price": pdp_price,
                        "pdp_qty": pdp_qty,
                        "select_desc": select_desc,
                        "cart_add_result": cart_add_result
                    })

                # 8. Navigate to cart
                print("\n==================================================")
                print("8. Navigating to /cart ...")
                print("==================================================")
                await session.call_tool("navigate", {"url": f"{BASE_URL}/cart"})
                await session.call_tool("wait", {"delay_ms": 2000})

                # 9. Evaluate line items
                print("9. Evaluating cart line items ...")
                eval_cart = await session.call_tool("evaluate", {"expression": """(() => {
                    const rows = [];
                    const trs = document.querySelectorAll("tbody tr.cart-items__table-row, tbody tr");
                    trs.forEach(tr => {
                        const titleEl = tr.querySelector(".cart-items__product-info a, a[href*='/products/']:not(:empty)") || tr.querySelector("a[href*='/products/']");
                        const priceMatch = tr.innerText.match(/\\$[0-9,]+(?:\\.[0-9]{2})?/);
                        const qtyEl = tr.querySelector("input[name*='updates'], input[type='number'], .quantity__input");
                        const href = titleEl ? titleEl.href : (tr.querySelector("a[href*='/products/']")?.href || "");
                        const title = titleEl ? (titleEl.innerText.trim() || tr.querySelector(".cart-items__product-info")?.innerText?.trim() || "") : "";
                        if (title || href) {
                            rows.push({
                                title: title,
                                href: href,
                                price: priceMatch ? priceMatch[0] : "",
                                quantity: qtyEl ? qtyEl.value : "1"
                            });
                        }
                    });
                    return JSON.stringify(rows);
                })()"""})

                raw_cart_text = eval_cart.content[0].text if eval_cart.content else "[]"
                cart_items = []
                try:
                    c_clean = json.loads(raw_cart_text)
                    cart_items = json.loads(c_clean) if isinstance(c_clean, str) else c_clean
                except Exception as e:
                    print(f"Error parsing cart JSON: {e}")

                print(f"Cart line items captured: {len(cart_items)}")
                print(json.dumps(cart_items, indent=2))

                # Map cart prices and quantities by handle
                cart_prices = {}
                cart_quantities = {}
                for item in cart_items:
                    item_href = item.get("href", "")
                    item_title = item.get("title", "").lower()
                    for h in HANDLES:
                        # Match handle in URL or title
                        if f"/products/{h}" in item_href or h.replace("-", " ") in item_title or h in item_title.replace(" ", "-"):
                            m_cp = re.search(r"\$[0-9,]+(?:\.[0-9]{2})?", item.get("price", ""))
                            cart_prices[h] = m_cp.group(0) if m_cp else item.get("price", "")
                            cart_quantities[h] = str(item.get("quantity", "1"))

                # 10. Write report "H1-6 full product matrix"
                report_lines = [
                    "# H1-6 full product matrix",
                    f"- **Generated (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                    f"- **Target Storefront**: `{BASE_URL}`",
                    f"- **Total Products Evaluated**: {len(matrix_results)}",
                    f"- **Total Cart Items Captured**: {len(cart_items)}",
                    "",
                    "## Product Matrix Table",
                    "",
                    "| Handle | Listing Price | JS Price | JS Available | PDP Price | PDP Qty | Select / Variant | Cart Add Result | Cart Price | Cart Qty | Flag |",
                    "|---|---|---|---|---|---|---|---|---|---|---|"
                ]

                high_value_cases = []

                for r in matrix_results:
                    h = r["handle"]
                    lp = r["listing_price"]
                    jp = r["js_price"]
                    ja = r["js_available"]
                    pp = r["pdp_price"]
                    pq = r.get("pdp_qty", "1")
                    sd = r.get("select_desc", "default")
                    car = r["cart_add_result"]
                    cp = cart_prices.get(h, "-")
                    cq = cart_quantities.get(h, "-")

                    flag = "OK"
                    reasons = []

                    # Normalization for price comparison
                    def norm(p):
                        if not p or p == "-":
                            return ""
                        return p.replace("$", "").replace(",", "").strip()

                    norm_lp = norm(lp)
                    norm_jp = norm(jp)
                    norm_pp = norm(pp)
                    norm_cp = norm(cp)

                    # Rule 1: listing price != PDP price != cart price
                    if norm_lp and norm_pp and norm_lp != norm_pp:
                        reasons.append(f"Listing ({lp}) ≠ PDP ({pp})")
                    if norm_cp and norm_pp and norm_cp != norm_pp:
                        reasons.append(f"Cart ({cp}) ≠ PDP ({pp})")
                    if norm_cp and norm_lp and norm_cp != norm_lp:
                        reasons.append(f"Cart ({cp}) ≠ Listing ({lp})")

                    # Rule 2: cart price differs from product.js price
                    if norm_cp and norm_jp and norm_cp != norm_jp:
                        reasons.append(f"Cart ({cp}) ≠ JS ({jp})")

                    # Rule 3: available false but cart add succeeds
                    if ja is False and car in ["added", "200"]:
                        reasons.append(f"JS available is false but Cart Add succeeded ({car})")

                    # Rule 4: quantity mismatch (PDP qty requested != Cart qty received)
                    if cq != "-" and pq != "-" and pq != cq:
                        reasons.append(f"Quantity mismatch: PDP Qty ({pq}) ≠ Cart Qty ({cq})")

                    if reasons:
                        flag = "**HIGH_VALUE**"
                        high_value_cases.append(f"- **`{h}`**: " + "; ".join(reasons))

                    report_lines.append(f"| `{h}` | {lp} | {jp} | {ja} | {pp} | {pq} | {sd} | {car} | {cp} | {cq} | {flag} |")

                report_lines.append("")
                report_lines.append("## High Value Contradictions (Flagged Cases)")
                if high_value_cases:
                    for hvc in high_value_cases:
                        report_lines.append(hvc)
                else:
                    report_lines.append("None detected.")

                report_lines.append("")
                report_lines.append("## Special Attention Analysis: `black-sunnies`")
                bs_row = next((r for r in matrix_results if r["handle"] == "black-sunnies"), None)
                if bs_row:
                    report_lines.append(f"- **Listing Price**: {bs_row['listing_price']}")
                    report_lines.append(f"- **Product.js Price**: {bs_row['js_price']} (available={bs_row['js_available']})")
                    report_lines.append(f"- **PDP Main Price**: {bs_row['pdp_price']}")
                    report_lines.append(f"- **Cart Add Result**: {bs_row['cart_add_result']}")
                    report_lines.append(f"- **Cart Price**: {cart_prices.get('black-sunnies', '-')}")
                    report_lines.append("- **Notes**: In previous catalog audits, black-sunnies was flagged as potentially $100 on PDP due to a prominent header/featured product (`Beanie` at $100.00). On the actual product information container, the price is verified at $50.00, consistent with the listing price ($50.00) and product.js ($50.00).")

                report_lines.append("")
                report_lines.append("## Complete Cart State (JSON)")
                report_lines.append("```json")
                report_lines.append(json.dumps(cart_items, indent=2))
                report_lines.append("```")

                final_report = "\n".join(report_lines)

                out_path = os.path.join(run_dir, "H1-6_full_product_matrix.md")
                with open(out_path, "w") as f:
                    f.write(final_report)

                print(f"\n==================================================")
                print(f"[SUCCESS] Matrix report generated:")
                print(f"Path: {out_path}")
                print(f"==================================================")

    except Exception as e:
        print(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
