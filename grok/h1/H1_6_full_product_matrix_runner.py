import os
import re
import json
import time
import datetime
import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8000/sse/?token=ph_live_D2aZuYtdGL6tUfuV2egoxp"

STORE_A = "https://funk-it-up-sdzgxmea.myshopify.com"
STORE_B = "https://xxxxxx-r48zg9i1.myshopify.com"

# H1-6 primitives (Store A test-data class)
PRIMITIVES_A = [
    "the-hidden-snowboard",
    "the-archived-snowboard",
    "the-compare-at-price-snowboard",
    "selling-plans-ski-wax",
    "gift-card",
    "the-out-of-stock-snowboard",
    "the-inventory-not-tracked-snowboard",
]

HANDLES_B_FALLBACK = [
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
    "soft-cotton-hoodie-in-violet",
]

LISTING_PRICES_B = {
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
    "soft-cotton-hoodie-in-violet": "$90.00",
}

HIDDEN_ARCHIVED = {"the-hidden-snowboard", "the-archived-snowboard"}


def find_add_to_cart_ref(snapshot_text):
    # AX snapshot pattern: [ax39: BUTTON 'Add to cart']
    m_ax = re.search(r"\[((?:ax|e)\d+):\s+BUTTON\s+'Add to cart'\]", snapshot_text, re.I)
    if m_ax:
        return m_ax.group(1)
    m_ax_gen = re.search(r"\[((?:ax|e)\d+):\s+(?:BUTTON|INPUT)[^\]]*'Add to cart'[^\]]*\]", snapshot_text, re.I)
    if m_ax_gen:
        return m_ax_gen.group(1)
    m = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)\s+'add'\]\s*Add to cart", snapshot_text, re.I)
    if m:
        return m.group(1)
    matches = re.findall(
        r"\[(e\d+):\s+(?:BUTTON|INPUT)[^\]]*\]\s*Add to cart(?!\s*\(\s*\d+\s*\))",
        snapshot_text,
        re.I,
    )
    if matches:
        return matches[0]
    m = re.search(r"\[(e\d+):\s+(?:BUTTON|INPUT)[^\]]*\]\s*Add to cart", snapshot_text, re.I)
    if m:
        return m.group(1)
    return None


def _tool_text(res):
    return res.content[0].text if res and res.content else ""


def _coerce_json(raw):
    if raw is None:
        return {}
    if isinstance(raw, (dict, list)):
        return raw
    text = str(raw).strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text[:800]}
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    return data


async def eval_json(session, expression):
    res = await session.call_tool("evaluate", {"expression": expression})
    return _coerce_json(_tool_text(res) or "{}")


async def navigate_and_parse_json(session, url):
    await session.call_tool("navigate", {"url": url})
    await session.call_tool("wait", {"delay_ms": 900})
    st = await page_state(session)
    if "Just a moment" in str(st.get("title", "")):
        return {"_cloudflare": True, **st}
    if st.get("hasPasswordForm") or "/password" in str(st.get("path", "")):
        return {"_gate": True, **st}
    data = await eval_json(
        session,
        "(document.querySelector('pre') || document.body).innerText",
    )
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        text = data.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", text, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    pass
            return {"error": "parse", "raw": text[:400]}
    return {"error": "parse", "raw": str(data)[:400]}


def _storefront_password():
    env = os.environ.get("STOREFRONT_PASSWORD")
    if env:
        return env
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    unlock = os.path.join(root, "unlock.py")
    try:
        text = open(unlock, encoding="utf-8").read()
        m = re.search(r'call_tool\("type",\s*\{[^}]*"text":\s*"([^"]+)"', text)
        return m.group(1) if m else ""
    except OSError:
        return ""


async def page_state(session):
    return await eval_json(
        session,
        """JSON.stringify({
            href: location.href,
            title: document.title,
            path: location.pathname,
            hasPasswordForm: !!document.querySelector('input[type=password],input[name=password]')
        })""",
    )


async def unlock_if_needed(session, base, run_dir):
    await session.call_tool("navigate", {"url": f"{base}/password"})
    await session.call_tool("wait", {"delay_ms": 1500})
    st = await page_state(session)
    if "Just a moment" in str(st.get("title", "")):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("CLOUDFLARE_CAPTCHA_DETECTED")
        return "CLOUDFLARE"
    if not st.get("hasPasswordForm") and "/password" not in str(st.get("path", "")):
        return "OPEN"
    pwd = _storefront_password()
    if not pwd:
        return "GATE"
    payload = json.dumps(pwd)
    await session.call_tool(
        "evaluate",
        {
            "expression": f"""(() => {{
                const inp = document.querySelector('input[type=password], input[name=password]');
                if (!inp) return JSON.stringify({{ok:false, reason:'no-input'}});
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(inp, {payload});
                inp.dispatchEvent(new Event('input', {{bubbles:true}}));
                inp.dispatchEvent(new Event('change', {{bubbles:true}}));
                const form = inp.form || document.querySelector('form[action*="password"]') || document.querySelector('form');
                if (form) {{ form.submit(); return JSON.stringify({{ok:true, via:'submit'}}); }}
                return JSON.stringify({{ok:false, reason:'no-form'}});
            }})()"""
        },
    )
    await session.call_tool("wait", {"delay_ms": 3500})
    st2 = await page_state(session)
    if not st2.get("hasPasswordForm") and "/password" not in str(st2.get("path", "")):
        return "UNLOCKED"
    html = _tool_text(await session.call_tool("get_snapshot", {"mode": "ax"}))
    pwd_ref = "ax13"
    m_pwd = re.search(
        r"\[((?:ax|e)\d+):\s+(?:INPUT|TEXTBOX|TEXTFIELD)[^\]]*?(?:password|Enter store using password|Enter store password)[^\]]*?\]",
        html,
        re.I,
    )
    if m_pwd:
        pwd_ref = m_pwd.group(1)
    btn_ref = "ax15"
    m_btn = re.search(
        r"\[((?:ax|e)\d+):\s+(?:BUTTON|INPUT)[^\]]*?(?:Enter|Submit)[^\]]*?\]",
        html,
        re.I,
    )
    if m_btn:
        btn_ref = m_btn.group(1)
    await session.call_tool("type", {"ref": pwd_ref, "text": pwd, "clear": True})
    await session.call_tool("click", {"ref": btn_ref})
    await session.call_tool("wait", {"delay_ms": 3500})
    st3 = await page_state(session)
    if st3.get("hasPasswordForm") or "/password" in str(st3.get("path", "")):
        return "GATE-STUCK"
    return "UNLOCKED"


async def harvest_handles(session, base):
    await session.call_tool("navigate", {"url": f"{base}/collections/all"})
    await session.call_tool("wait", {"delay_ms": 2000})
    st = await page_state(session)
    if st.get("hasPasswordForm") or "/password" in str(st.get("path", "")):
        return [], st, True
    data = await eval_json(
        session,
        """JSON.stringify({
            href: location.href,
            title: document.title,
            handles: [...new Set([...document.querySelectorAll("a[href*='/products/']")]
                .map(a => {
                    const m = (a.pathname || '').match(/\\/products\\/([^/?#]+)/);
                    return m ? decodeURIComponent(m[1]) : null;
                })
                .filter(Boolean))]
        })""",
    )
    handles = data.get("handles") if isinstance(data, dict) else []
    listed_hidden = "the-hidden-snowboard" in handles
    listed_archived = "the-archived-snowboard" in handles
    return handles, {**st, **data, "listed_hidden": listed_hidden, "listed_archived": listed_archived}, False


async def fetch_cart_js(session, base):
    data = await navigate_and_parse_json(session, f"{base}/cart.js")
    if isinstance(data, dict) and isinstance(data.get("json"), dict) and "items" in data.get("json"):
        return data["json"]
    return data if isinstance(data, dict) else {"error": "parse"}


def _cents_to_price(cents):
    try:
        return f"${float(cents) / 100:.2f}"
    except (TypeError, ValueError):
        return str(cents or "")


def apply_cart_item(row, item):
    if not isinstance(item, dict):
        return
    row["cart_line"] = True
    cents = item.get("final_price") or item.get("price") or item.get("line_price") or 0
    row["cart_line_price"] = _cents_to_price(cents)
    row["cart_line_qty"] = str(item.get("quantity", "1"))
    if item.get("available") is not None:
        row["add_js_available"] = item.get("available")


def item_matches_handle(item, handle):
    if not isinstance(item, dict):
        return False
    url = str(item.get("url") or "")
    return f"/products/{handle}" in url or item.get("handle") == handle


def norm_price(p):
    if not p or p == "-":
        return ""
    return str(p).replace("$", "").replace(",", "").strip()


async def process_handle(session, base, handle, listing_price, store_id, run_dir):
    row = {
        "store": store_id,
        "handle": handle,
        "listing_price": listing_price,
        "js_price": "",
        "js_available": None,
        "js_variants_count": 0,
        "js_variant_id": "",
        "pdp_price": "",
        "pdp_qty": "1",
        "select_desc": "default",
        "compare_at_visible": False,
        "sold_out_text": False,
        "has_add_form": False,
        "cart_add_result": "none",
        "cart_line": False,
        "cart_line_price": "-",
        "cart_line_qty": "-",
        "add_js_status": None,
        "add_js_price": "",
        "add_js_qty": "",
        "add_js_available": None,
        "gate": False,
        "href": "",
        "title": "",
        "latency_ms": 0,
        "flags": [],
    }
    t0 = time.perf_counter()
    prod_resp = await navigate_and_parse_json(session, f"{base}/products/{handle}.js")
    if isinstance(prod_resp, dict) and prod_resp.get("_cloudflare"):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("CLOUDFLARE_CAPTCHA_DETECTED")
        row["flags"].append("CLOUDFLARE")
        row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return row, True
    if isinstance(prod_resp, dict) and prod_resp.get("_gate"):
        row["gate"] = True
        row["cart_add_result"] = "password_gate"
        row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return row, False
    prod_data = prod_resp if isinstance(prod_resp, dict) else None
    if isinstance(prod_data, dict) and prod_data.get("error"):
        row["flags"].append("js_fetch_error")
    if isinstance(prod_data, dict) and prod_data.get("price") is not None:
        row["js_price"] = _cents_to_price(prod_data.get("price"))
        row["js_available"] = prod_data.get("available")
        variants = prod_data.get("variants") or []
        row["js_variants_count"] = len(variants)
        if variants:
            row["js_variant_id"] = str(variants[0].get("id") or "")
            if variants[0].get("available") is not None and row["js_available"] is None:
                row["js_available"] = variants[0].get("available")

    pdp_url = f"{base}/products/{handle}"
    await session.call_tool("navigate", {"url": pdp_url})
    await session.call_tool("wait", {"delay_ms": 1500})
    st = await page_state(session)
    row["href"] = st.get("href", pdp_url)
    row["title"] = st.get("title", "")
    if "/checkout" in str(st.get("href", "")):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("CHECKOUT_OPENED")
        row["flags"].append("CHECKOUT")
        return row, True
    if st.get("hasPasswordForm") or "/password" in str(st.get("path", "")):
        row["gate"] = True
        row["cart_add_result"] = "password_gate"
        row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return row, False

    pdp_info = await eval_json(
        session,
        """(() => {
            const bodyText = document.body ? document.body.innerText : "";
            let mainEl = document.querySelector('main, .product, .product__info-container');
            let el = mainEl ? mainEl.querySelector('.price-item--regular, .price, .product__price, [data-product-price]') : null;
            if (!el) el = document.querySelector('.price-item--regular, .price');
            let priceText = el ? el.innerText.trim() : '';
            let qtyEl = document.querySelector('input[name="quantity"], .quantity__input, [data-quantity-input]');
            let qtyVal = qtyEl ? qtyEl.value : '1';
            let selOption = '';
            let selEl = document.querySelector('select[name="id"], variant-selects select, .product-form select');
            if (selEl && selEl.options && selEl.selectedIndex >= 0) {
                selOption = selEl.options[selEl.selectedIndex].text.trim();
            }
            if (!selOption) {
                let checkedRadio = document.querySelector('variant-radios input[type="radio"]:checked, fieldset input[type="radio"]:checked');
                if (checkedRadio) selOption = checkedRadio.value;
            }
            let varIdEl = document.querySelector('form[action*="/cart/add"] input[name="id"]');
            return JSON.stringify({
                price: priceText,
                qty: qtyVal,
                selected_option: selOption,
                variant_id: varIdEl ? varIdEl.value : '',
                compare_at: /compare-at|compare at|\\bwas\\b/i.test(bodyText),
                sold_out: /sold out|out of stock|unavailable/i.test(bodyText),
                has_add_form: !!document.querySelector('form[action*="/cart/add"]')
            });
        })()""",
    )
    if not isinstance(pdp_info, dict):
        pdp_info = {}
    pdp_price_text = str(pdp_info.get("price", ""))
    m_pdp = re.search(r"\$[0-9,]+(?:\.[0-9]{2})?", pdp_price_text)
    row["pdp_price"] = m_pdp.group(0) if m_pdp else pdp_price_text
    row["pdp_qty"] = str(pdp_info.get("qty", "1"))
    sel = pdp_info.get("selected_option") or ""
    vid = str(pdp_info.get("variant_id") or row["js_variant_id"] or "")
    if vid and not row["js_variant_id"]:
        row["js_variant_id"] = vid
    row["select_desc"] = sel if sel else (f"id:{vid}" if vid else "default")
    row["compare_at_visible"] = bool(pdp_info.get("compare_at"))
    row["sold_out_text"] = bool(pdp_info.get("sold_out"))
    row["has_add_form"] = bool(pdp_info.get("has_add_form"))

    snap = _tool_text(await session.call_tool("get_snapshot", {"mode": "ax"}))
    btn_ref = find_add_to_cart_ref(snap)
    if btn_ref:
        await session.call_tool("click", {"ref": btn_ref})
        await session.call_tool("wait", {"delay_ms": 1500})
        cart_data = await eval_json(
            session,
            """JSON.stringify({
                href: location.href,
                error: (() => {
                    let errEl = document.querySelector('.product-form__error-message-wrapper:not([hidden]), .form__message--error, .product-form__error-message');
                    return (errEl && !errEl.closest('[hidden]')) ? errEl.innerText.trim() : "";
                })(),
                cart_count: (() => {
                    let countEl = document.querySelector('.cart-count-bubble, .header__cart-count, [data-cart-count], .cart-link__bubble');
                    return countEl ? countEl.innerText.trim() : "";
                })(),
                drawer_visible: !!document.querySelector('cart-notification.animate, cart-drawer.animate, .drawer.active')
            })""",
        )
        if not isinstance(cart_data, dict):
            cart_data = {}
        if "/checkout" in str(cart_data.get("href", "")):
            with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
                f.write("CHECKOUT_OPENED")
            row["flags"].append("CHECKOUT")
            return row, True
        if cart_data.get("error"):
            row["cart_add_result"] = f"error: {cart_data.get('error')}"
        elif cart_data.get("cart_count") or cart_data.get("drawer_visible") or "/cart" in str(cart_data.get("href", "")):
            row["cart_add_result"] = "added"
        else:
            row["cart_add_result"] = "200"
    elif row["has_add_form"] and row["js_variant_id"]:
        row["cart_add_result"] = "no_click_ref"

    async def post_add_form():
        if not row["js_variant_id"]:
            return
        vid = str(row["js_variant_id"])
        await session.call_tool(
            "evaluate",
            {
                "expression": f"""(() => {{
                    const f = document.createElement('form');
                    f.method = 'POST';
                    f.action = '/cart/add';
                    f.style.display = 'none';
                    const id = document.createElement('input');
                    id.name = 'id';
                    id.value = {json.dumps(vid)};
                    const qty = document.createElement('input');
                    qty.name = 'quantity';
                    qty.value = '1';
                    f.appendChild(id);
                    f.appendChild(qty);
                    document.body.appendChild(f);
                    f.submit();
                    return 'submitted';
                }})()"""
            },
        )
        await session.call_tool("wait", {"delay_ms": 2000})
        st_add = await page_state(session)
        if "/checkout" in str(st_add.get("href", "")):
            with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
                f.write("CHECKOUT_OPENED")
            row["flags"].append("CHECKOUT")
            return True
        row["cart_add_result"] = "added_form"
        row["add_js_status"] = 200
        return False

    async def read_cart_line():
        cart = await fetch_cart_js(session, base)
        if isinstance(cart, dict) and cart.get("_cloudflare"):
            return True
        if isinstance(cart, dict) and cart.get("_gate"):
            row["gate"] = True
            return False
        items = cart.get("items") if isinstance(cart, dict) else None
        if isinstance(items, list):
            for item in items:
                if item_matches_handle(item, handle):
                    apply_cart_item(row, item)
                    row["add_js_price"] = row.get("add_js_price") or row.get("cart_line_price") or ""
                    row["add_js_qty"] = row.get("add_js_qty") or row.get("cart_line_qty") or ""
                    return False
        return False

    hard = await read_cart_line()
    if hard:
        row["flags"].append("CLOUDFLARE")
        return row, True
    if not row.get("cart_line") and row.get("js_variant_id"):
        add_result = str(row.get("cart_add_result") or "")
        if not add_result.startswith("error:"):
            stopped = await post_add_form()
            if stopped:
                return row, True
            hard = await read_cart_line()
            if hard:
                row["flags"].append("CLOUDFLARE")
                return row, True

    row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return row, False


def score_row(row, collections_meta):
    flags = list(row.get("flags") or [])
    nlp = norm_price(row.get("listing_price"))
    njp = norm_price(row.get("js_price"))
    npp = norm_price(row.get("pdp_price"))
    ncp = norm_price(row.get("cart_line_price"))
    nap = norm_price(row.get("add_js_price"))
    handle = row["handle"]
    money = bool(row.get("cart_line"))

    if row.get("gate"):
        return flags, False, "gate"

    if nlp and npp and nlp != npp:
        flags.append("listing_ne_pdp")
    if money and ncp and npp and ncp != npp:
        flags.append("cart_ne_pdp")
    if money and ncp and nlp and ncp != nlp:
        flags.append("cart_ne_listing")
    if money and ncp and njp and ncp != njp:
        flags.append("cart_ne_js")
    if money and nap and npp and nap != npp:
        flags.append("addjs_ne_pdp")
    if money and nap and nlp and nap != nlp:
        flags.append("addjs_ne_listing")
    if money and nap and njp and nap != njp:
        flags.append("addjs_ne_js")
    if money and nap and ncp and nap != ncp:
        flags.append("addjs_ne_cart")
    if row.get("js_available") is False and row.get("cart_add_result") in ("added", "200", "added_js") and money:
        flags.append("unavailable_but_carted")
    if row.get("sold_out_text") and money:
        flags.append("sold_out_text_but_carted")
    pq, cq = str(row.get("pdp_qty", "1")), str(row.get("cart_line_qty", "-"))
    if money and cq != "-" and pq != "-" and pq != cq:
        flags.append("qty_mismatch")
    if handle in HIDDEN_ARCHIVED and money:
        flags.append("hidden_or_archived_purchasable")
    if handle in HIDDEN_ARCHIVED and not money:
        flags.append("hidden_or_archived_public_price_no_line")
    if handle == "the-compare-at-price-snowboard" and row.get("compare_at_visible") and money:
        flags.append("compare_at_carted")
    listed_hidden = bool(collections_meta.get("listed_hidden"))
    listed_archived = bool(collections_meta.get("listed_archived"))
    if handle == "the-hidden-snowboard" and listed_hidden:
        flags.append("collections_lists_hidden")
    if handle == "the-archived-snowboard" and listed_archived:
        flags.append("collections_lists_archived")

    # Spec: ticket only if money moved or publish-state contradiction with a cart line.
    ticket = any(
        f in flags
        for f in (
            "cart_ne_pdp",
            "cart_ne_listing",
            "cart_ne_js",
            "addjs_ne_pdp",
            "addjs_ne_listing",
            "addjs_ne_js",
            "addjs_ne_cart",
            "unavailable_but_carted",
            "sold_out_text_but_carted",
            "qty_mismatch",
            "hidden_or_archived_purchasable",
        )
    )
    return flags, ticket, "ticket" if ticket else ("informational" if flags else "ok")


async def run_store(session, store_id, base, handles, listing_map, run_dir):
    print(f"\n[*] Store {store_id} unlock {base}")
    unlock = await unlock_if_needed(session, base, run_dir)
    print(f"    unlock={unlock}")
    if unlock == "CLOUDFLARE":
        return [], {"unlock": unlock}, True
    if unlock in ("GATE", "GATE-STUCK"):
        return [
            {
                "store": store_id,
                "handle": "_store_",
                "gate": True,
                "cart_add_result": unlock,
                "flags": [unlock],
                "latency_ms": 0,
            }
        ], {"unlock": unlock}, False

    print(f"    clearing cart")
    await session.call_tool("navigate", {"url": f"{base}/cart/clear"})
    await session.call_tool("wait", {"delay_ms": 800})

    harvested, collections_meta, gated = await harvest_handles(session, base)
    collections_meta = collections_meta if isinstance(collections_meta, dict) else {}
    collections_meta["unlock"] = unlock
    collections_meta["harvested_count"] = len(harvested)
    if gated:
        collections_meta["unlock"] = "GATE_AFTER_UNLOCK"
        return [], collections_meta, False

    use_handles = harvested or list(handles)
    # Always include primitives on Store A even if collection omitted them.
    if store_id == "A":
        for h in PRIMITIVES_A:
            if h not in use_handles:
                use_handles.append(h)

    rows = []
    for idx, handle in enumerate(use_handles, 1):
        print(f"    [{idx}/{len(use_handles)}] {store_id}:{handle}")
        row, hard = await process_handle(
            session, base, handle, listing_map.get(handle, ""), store_id, run_dir
        )
        flags, ticket, status = score_row(row, collections_meta)
        row["flags"] = flags
        row["ticket_candidate"] = ticket
        row["status"] = status
        rows.append(row)
        print(
            f"      js={row.get('js_price')} pdp={row.get('pdp_price')} "
            f"add={row.get('cart_add_result')} line={row.get('cart_line')} "
            f"status={status}"
        )
        if hard:
            return rows, collections_meta, True
    return rows, collections_meta, False


async def main():
    utc_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_str}"
    os.makedirs(run_dir, exist_ok=True)
    print(f"[*] H1-6 wider matrix → {run_dir}")

    all_rows = []
    meta = {"A": {}, "B": {}}
    hard_stop = False

    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            rows_a, meta_a, hard = await run_store(
                session, "A", STORE_A, PRIMITIVES_A, {}, run_dir
            )
            meta["A"] = meta_a
            all_rows.extend(rows_a)
            if hard:
                hard_stop = True
            else:
                rows_b, meta_b, hard = await run_store(
                    session, "B", STORE_B, HANDLES_B_FALLBACK, LISTING_PRICES_B, run_dir
                )
                meta["B"] = meta_b
                all_rows.extend(rows_b)
                hard_stop = hard

    tickets = [r for r in all_rows if r.get("ticket_candidate")]
    informational = [
        r
        for r in all_rows
        if r.get("status") == "informational" or "hidden_or_archived_public_price_no_line" in (r.get("flags") or [])
    ]

    evaluate_data = {
        "timestamp_utc": utc_str,
        "hypothesis": "H1-6",
        "source": "local-chrome",
        "spec": {
            "asset": "your-store.myshopify.com",
            "in_scope": True,
            "bounty_eligible": True,
            "self_created_store_required": True,
            "stores": {
                "A": STORE_A.replace("https://", ""),
                "B": STORE_B.replace("https://", ""),
            },
            "support_contact": False,
            "cdn_claim": False,
            "checkout_clicked": False,
            "ticket_rule": "price/stock/publish contradiction that creates a cart line (money movement); public hidden/archived price without a line is informational",
        },
        "hard_stop": hard_stop,
        "summary": {
            "total_checks": len(all_rows),
            "ticket_candidates": len(tickets),
            "informational": len(informational),
            "store_A_unlock": meta.get("A", {}).get("unlock"),
            "store_B_unlock": meta.get("B", {}).get("unlock"),
            "store_A_harvested": meta.get("A", {}).get("harvested_count"),
            "store_B_harvested": meta.get("B", {}).get("harvested_count"),
            "collections_lists_hidden": bool(meta.get("A", {}).get("listed_hidden")),
            "collections_lists_archived": bool(meta.get("A", {}).get("listed_archived")),
        },
        "ticket_candidates": [
            {
                "store": r["store"],
                "handle": r["handle"],
                "flags": r.get("flags"),
                "js_price": r.get("js_price"),
                "pdp_price": r.get("pdp_price"),
                "cart_line": r.get("cart_line"),
                "cart_line_price": r.get("cart_line_price"),
                "cart_add_result": r.get("cart_add_result"),
                "js_available": r.get("js_available"),
            }
            for r in tickets
        ],
        "results": all_rows,
        "collections": meta,
    }

    eval_path = os.path.join(run_dir, "evaluate.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(evaluate_data, f, indent=2)

    protocol = {
        "timestamp": utc_str,
        "target": "H1-6 wider storefront ticket-candidate matrix",
        "server_url": "http://127.0.0.1:8000/sse/?token=redacted",
        "source": "local-phantom+chrome",
        "sessions": 1,
        "verdict": "ticket-candidate" if tickets else "no-ticket",
        "reason": (
            f"{len(tickets)} cart-backed contradictions"
            if tickets
            else "No money-moving price/stock/publish contradiction; hidden/archived public price without a line is informational per spec/roadmap."
        ),
        "results": [
            {
                "tool": f"{r.get('store')}:{r.get('handle')}",
                "status": "CANDIDATE" if r.get("ticket_candidate") else str(r.get("status", "ok")).upper(),
                "latency_ms": r.get("latency_ms"),
                "details": f"add={r.get('cart_add_result')} line={r.get('cart_line')} flags={r.get('flags')}",
            }
            for r in all_rows
        ],
    }
    with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2)

    md = [
        f"# H1-6 wider product matrix — {utc_str}",
        "",
        f"- **Spec asset**: `your-store.myshopify.com` (in-scope, bounty-eligible, self-created stores only)",
        f"- **Stores**: A `{STORE_A}` · B `{STORE_B}`",
        f"- **Ticket candidates**: `{len(tickets)}`",
        f"- **Verdict**: `{'ticket-candidate' if tickets else 'no-ticket'}`",
        f"- **Unlock A/B**: `{meta.get('A', {}).get('unlock')}` / `{meta.get('B', {}).get('unlock')}`",
        "",
        "## Matrix",
        "",
        "| Store | Handle | JS Price | Available | PDP Price | Add | Cart line | Cart price | Flags | Status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in all_rows:
        md.append(
            f"| `{r.get('store')}` | `{r.get('handle')}` | {r.get('js_price') or '-'} | {r.get('js_available')} | "
            f"{r.get('pdp_price') or '-'} | {r.get('cart_add_result')} | {r.get('cart_line')} | "
            f"{r.get('cart_line_price')} | {','.join(r.get('flags') or []) or '-'} | **{r.get('status')}** |"
        )
    md.extend(
        [
            "",
            "## Ticket candidates (spec-eligible)",
            "",
        ]
    )
    if tickets:
        for r in tickets:
            md.append(f"- `{r['store']}:{r['handle']}` flags={r.get('flags')} line={r.get('cart_line_price')}")
    else:
        md.append("None. Hidden/archived public prices without a cart line stay informational.")
    md.extend(
        [
            "",
            "## Spec mapping",
            "- In scope: researcher `*.myshopify.com` only.",
            "- Out: Support, CDN upload, third-party merchants, checkout click.",
            "- Impact bar: contradiction that moves money (cart line), not title-only test-data.",
            "",
        ]
    )
    content = "\n".join(md)
    with open(os.path.join(run_dir, "MATRIX.md"), "w", encoding="utf-8") as f:
        f.write(content)
    with open(os.path.join(run_dir, "H1-6_full_product_matrix.md"), "w", encoding="utf-8") as f:
        f.write(content)
    with open(os.path.join(run_dir, "SMOKE.md"), "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] artifacts {run_dir} tickets={len(tickets)} hard_stop={hard_stop}")


if __name__ == "__main__":
    asyncio.run(main())
