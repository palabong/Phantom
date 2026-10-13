import os
import re
import json
import time
import datetime
import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = os.environ.get("PHANTOM_SSE_URL") or (
    "http://127.0.0.1:8000/sse/?token="
    + os.environ.get("PHANTOM_AUTH_TOKEN", "ph_live_local_verify")
)

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


def _same_host(base, href):
    return str(href or "").startswith(base + "/") or str(href or "").rstrip("/") == base.rstrip("/")


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


def _gate_refs(snapshot_text):
    """Password input and Enter submit from an HTML AOM snapshot.

    authenticity_token and the Log in here link are never selected.
    """
    password_ref = None
    enter_ref = None
    pattern = re.compile(r"\[(e\d+):\s+(INPUT|BUTTON|A)\s+'([^']*)'\]")
    matches = list(pattern.finditer(snapshot_text or ""))
    for i, match in enumerate(matches):
        ref, tag, context = match.group(1), match.group(2), match.group(3)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(snapshot_text)
        trail = snapshot_text[match.end():end]
        if tag == "INPUT" and context == "password":
            password_ref = ref
        elif tag == "BUTTON" and (
            context.lower() == "enter" or re.search(r"\bEnter\b", trail)
        ):
            enter_ref = ref
    return password_ref, enter_ref


def _redact(text, secret):
    if secret and secret in str(text):
        return str(text).replace(secret, "[REDACTED]")
    return str(text)


def _scrub_secret(secret):
    """Remove a gate secret from the engine log. Do not print it."""
    if not secret:
        return
    path = "/tmp/phantom_engine.log"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return
    if secret not in text:
        return
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text.replace(secret, "[REDACTED]"))


async def unlock_if_needed(session, base, run_dir, store_id):
    """Open the storefront. Store A may be unlocked once when PH_GATE_A is set.

    The secret is typed into the password input and submitted with Enter.
    It is not printed, archived, or retried. Store B is never typed.
    """
    await session.call_tool("navigate", {"url": f"{base}/"})
    await session.call_tool("wait", {"delay_ms": 1500})
    st = await page_state(session)
    if "Just a moment" in str(st.get("title", "")):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("CLOUDFLARE_CAPTCHA_DETECTED")
        return "CLOUDFLARE", False
    href = str(st.get("href", ""))
    if href and not _same_host(base, href):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("HOST_LEFT")
        return "HOST", False
    gated = st.get("hasPasswordForm") or "/password" in str(st.get("path", ""))
    if not gated:
        return "OPEN", False

    secret = os.environ.get("PH_GATE_A", "") if store_id == "A" else ""
    if not secret:
        return "GATE", False

    snap = await session.call_tool("get_snapshot", {"mode": "html"})
    password_ref, _enter_ref = _gate_refs(_tool_text(snap))
    if not password_ref:
        return "GATE-SHAPE", False
    try:
        await session.call_tool("type", {"ref": password_ref, "text": secret})
    except Exception as exc:
        print(f"    unlock_type_failed {_redact(exc, secret)}", flush=True)
        return "GATE-STUCK", True

    filled = await eval_json(
        session,
        """JSON.stringify({
            n: (document.querySelector('input[name=password]') || {value: ''}).value.length
        })""",
    )
    if not isinstance(filled, dict) or int(filled.get("n") or 0) != len(secret):
        # Char key events did not fill the field. Assign the value once, then submit.
        print("    unlock_field_assign", flush=True)
        expr = (
            "(() => { const el = document.querySelector('input[name=password]');"
            " if (!el) return JSON.stringify({ok:false,n:0});"
            " el.focus(); el.value = " + json.dumps(secret) + ";"
            " el.dispatchEvent(new Event('input', {bubbles:true}));"
            " el.dispatchEvent(new Event('change', {bubbles:true}));"
            " return JSON.stringify({ok:true,n:el.value.length}); })()"
        )
        try:
            filled = await eval_json(session, expr)
        finally:
            _scrub_secret(secret)
        if not isinstance(filled, dict) or int(filled.get("n") or 0) != len(secret):
            print("    unlock_field_empty", flush=True)
            return "GATE-STUCK", True

    snap = await session.call_tool("get_snapshot", {"mode": "html"})
    _password_ref, enter_ref = _gate_refs(_tool_text(snap))
    if not enter_ref:
        return "GATE-STUCK", True
    await session.call_tool("click", {"ref": enter_ref})
    await session.call_tool("wait", {"delay_ms": 8000})
    st = await page_state(session)
    if "Just a moment" in str(st.get("title", "")):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("CLOUDFLARE_CAPTCHA_DETECTED")
        return "CLOUDFLARE", True
    href = str(st.get("href", ""))
    if href and not _same_host(base, href):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("HOST_LEFT")
        return "HOST", True
    if st.get("hasPasswordForm") or "/password" in str(st.get("path", "")):
        return "GATE-STUCK", True
    return "OPEN", True


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


async def fetch_catalog_api(session, base, run_dir):
    """Ajax catalog: /products.json. This is the API surface, distinct from /products/{handle}.js."""
    data = await navigate_and_parse_json(session, f"{base}/products.json?limit=250")
    if not isinstance(data, dict):
        return {}, {"error": "parse"}
    if data.get("_cloudflare"):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("CLOUDFLARE_CAPTCHA_DETECTED")
        return {}, data
    if data.get("_gate"):
        return {}, data
    href = str(data.get("href") or "")
    if href and not _same_host(base, href):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("HOST_LEFT")
        return {}, {"_host": href}
    if not isinstance(data.get("products"), list):
        return {}, {"ok": False, "error": data.get("error") or "no_products_key"}
    products = data.get("products")
    index = {}
    for product in products:
        if not isinstance(product, dict) or not product.get("handle"):
            continue
        variants = product.get("variants") or []
        first = variants[0] if variants else {}
        price = first.get("price")
        available = first.get("available")
        if available is None:
            available = product.get("available")
        index[product["handle"]] = {
            "api_price": _dollar_price(price) if price is not None else "",
            "api_available": available,
            "api_variant_id": str(first.get("id") or ""),
            "api_variants_count": len(variants),
        }
    return index, {"ok": True, "count": len(index)}


def _cents_to_price(cents):
    """Product .js prices are integer cents."""
    try:
        return f"${float(cents) / 100:.2f}"
    except (TypeError, ValueError):
        return str(cents or "")


def _dollar_price(value):
    """products.json prices are decimal currency strings, not cents."""
    try:
        return f"${float(str(value).replace(',', '').strip()):.2f}"
    except (TypeError, ValueError):
        return str(value or "")


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


async def process_handle(session, base, handle, api_product, store_id, run_dir):
    api_product = api_product or {}
    row = {
        "store": store_id,
        "handle": handle,
        "ui_price": "",
        "js_price": "",
        "api_price": api_product.get("api_price", ""),
        "api_available": api_product.get("api_available"),
        "api_variant_id": api_product.get("api_variant_id", ""),
        "api_missing": not bool(api_product),
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
    if row["href"] and not _same_host(base, row["href"]):
        with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
            f.write("HOST_LEFT")
        row["flags"].append("HOST")
        row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return row, True
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
    row["ui_price"] = row["pdp_price"]
    row["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return row, False


DISCREPANCY_FLAGS = (
    "ui_ne_json",
    "ui_ne_api",
    "json_ne_api",
    "availability_ui_ne_json",
    "availability_ui_ne_api",
    "availability_json_ne_api",
    "api_omits_ui_json",
)


def score_row(row, collections_meta):
    flags = list(row.get("flags") or [])
    ui = norm_price(row.get("ui_price") or row.get("pdp_price"))
    js = norm_price(row.get("js_price"))
    api = norm_price(row.get("api_price"))
    handle = row["handle"]

    if row.get("gate"):
        return flags, False, "gate"

    if ui and js and ui != js:
        flags.append("ui_ne_json")
    if ui and api and ui != api:
        flags.append("ui_ne_api")
    if js and api and js != api:
        flags.append("json_ne_api")
    if row.get("catalog_ok") and row.get("api_missing") and (ui or js):
        flags.append("api_omits_ui_json")

    js_av = row.get("js_available")
    api_av = row.get("api_available")
    ui_sold = bool(row.get("sold_out_text"))
    ui_add = bool(row.get("has_add_form"))
    if js_av is True and ui_sold:
        flags.append("availability_ui_ne_json")
    if js_av is False and ui_add and not ui_sold:
        flags.append("availability_ui_ne_json")
    if api_av is True and ui_sold:
        flags.append("availability_ui_ne_api")
    if api_av is False and ui_add and not ui_sold:
        flags.append("availability_ui_ne_api")
    if api_av is not None and js_av is not None and bool(api_av) != bool(js_av):
        flags.append("availability_json_ne_api")

    if handle == "the-hidden-snowboard" and collections_meta.get("listed_hidden"):
        flags.append("collections_lists_hidden")
    if handle == "the-archived-snowboard" and collections_meta.get("listed_archived"):
        flags.append("collections_lists_archived")

    discrepancy = any(flag in flags for flag in DISCREPANCY_FLAGS)
    if discrepancy:
        return flags, True, "discrepancy"
    if flags:
        return flags, False, "informational"
    return flags, False, "ok"


async def run_store(session, store_id, base, handles, run_dir):
    print(f"\n[*] Store {store_id} observe {base}")
    unlock, password_typed = await unlock_if_needed(session, base, run_dir, store_id)
    print(f"    gate={unlock} password_typed={str(bool(password_typed)).lower()}")
    store_meta = {"unlock": unlock, "password_typed": bool(password_typed)}
    if unlock in ("CLOUDFLARE", "HOST"):
        return [], store_meta, True
    if unlock in ("GATE", "GATE-STUCK", "GATE-SHAPE"):
        return [
            {
                "store": store_id,
                "handle": "_store_",
                "gate": True,
                "flags": [unlock],
                "status": "gate",
                "latency_ms": 0,
            }
        ], store_meta, False

    api_index, api_meta = await fetch_catalog_api(session, base, run_dir)
    print(f"    api_products={api_meta.get('count', 0)}")
    if api_meta.get("_cloudflare") or api_meta.get("_host"):
        store_meta["api"] = api_meta
        return [], store_meta, True
    if api_meta.get("_gate"):
        store_meta["unlock"] = "GATE"
        store_meta["api"] = api_meta
        return [
            {
                "store": store_id,
                "handle": "_store_",
                "gate": True,
                "flags": ["GATE"],
                "status": "gate",
                "latency_ms": 0,
            }
        ], store_meta, False

    harvested, collections_meta, gated = await harvest_handles(session, base)
    collections_meta = collections_meta if isinstance(collections_meta, dict) else {}
    collections_meta["unlock"] = unlock
    collections_meta["password_typed"] = bool(password_typed)
    collections_meta["harvested_count"] = len(harvested)
    collections_meta["api_count"] = api_meta.get("count", 0)
    if gated:
        collections_meta["unlock"] = "GATE_AFTER_OPEN"
        collections_meta["password_typed"] = bool(password_typed)
        return [
            {
                "store": store_id,
                "handle": "_store_",
                "gate": True,
                "flags": ["GATE"],
                "status": "gate",
                "latency_ms": 0,
            }
        ], collections_meta, False

    use_handles = harvested or list(handles)
    if store_id == "A":
        for h in PRIMITIVES_A:
            if h not in use_handles:
                use_handles.append(h)

    rows = []
    for idx, handle in enumerate(use_handles, 1):
        print(f"    [{idx}/{len(use_handles)}] {store_id}:{handle}", flush=True)
        row, hard = await process_handle(
            session, base, handle, api_index.get(handle), store_id, run_dir
        )
        row["catalog_ok"] = bool(api_meta.get("ok"))
        flags, discrepancy, status = score_row(row, collections_meta)
        row["flags"] = flags
        row["discrepancy"] = discrepancy
        row["status"] = status
        rows.append(row)
        print(
            f"      ui={row.get('ui_price') or '-'} json={row.get('js_price') or '-'} "
            f"api={row.get('api_price') or '-'} status={status} flags={flags}",
            flush=True,
        )
        if hard:
            return rows, collections_meta, True
    return rows, collections_meta, False


async def main():
    utc_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_str}"
    os.makedirs(run_dir, exist_ok=False)
    print(f"[*] H1-6 UI/JSON/API discrepancy matrix → {run_dir}", flush=True)

    all_rows = []
    meta = {"A": {}, "B": {}}
    hard_stop = False

    try:
        async with sse_client(SSE_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                rows_a, meta_a, hard = await run_store(
                    session, "A", STORE_A, PRIMITIVES_A, run_dir
                )
                meta["A"] = meta_a
                all_rows.extend(rows_a)
                if hard:
                    hard_stop = True
                else:
                    rows_b, meta_b, hard = await run_store(
                        session, "B", STORE_B, HANDLES_B_FALLBACK, run_dir
                    )
                    meta["B"] = meta_b
                    all_rows.extend(rows_b)
                    hard_stop = hard
    finally:
        _scrub_secret(os.environ.get("PH_GATE_A", ""))

    discrepancies = [r for r in all_rows if r.get("discrepancy")]
    informational = [r for r in all_rows if r.get("status") == "informational"]

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
            "cart_mutated": False,
            "surfaces": {
                "ui": "PDP visible price and sold-out text",
                "json": "/products/{handle}.js",
                "api": "/products.json?limit=250",
            },
            "discrepancy_rule": "UI price or availability disagrees with product JSON or the products.json API",
        },
        "hard_stop": hard_stop,
        "summary": {
            "total_checks": len(all_rows),
            "discrepancies": len(discrepancies),
            "informational": len(informational),
            "store_A_unlock": meta.get("A", {}).get("unlock"),
            "store_B_unlock": meta.get("B", {}).get("unlock"),
            "store_A_password_typed": bool(meta.get("A", {}).get("password_typed")),
            "store_B_password_typed": bool(meta.get("B", {}).get("password_typed")),
            "store_A_harvested": meta.get("A", {}).get("harvested_count"),
            "store_B_harvested": meta.get("B", {}).get("harvested_count"),
            "store_A_api": meta.get("A", {}).get("api_count"),
            "store_B_api": meta.get("B", {}).get("api_count"),
            "collections_lists_hidden": bool(meta.get("A", {}).get("listed_hidden")),
            "collections_lists_archived": bool(meta.get("A", {}).get("listed_archived")),
        },
        "discrepancies": [
            {
                "store": r["store"],
                "handle": r["handle"],
                "flags": r.get("flags"),
                "ui_price": r.get("ui_price"),
                "js_price": r.get("js_price"),
                "api_price": r.get("api_price"),
                "js_available": r.get("js_available"),
                "api_available": r.get("api_available"),
                "sold_out_text": r.get("sold_out_text"),
                "has_add_form": r.get("has_add_form"),
                "href": r.get("href"),
            }
            for r in discrepancies
        ],
        "results": all_rows,
        "collections": meta,
    }

    eval_path = os.path.join(run_dir, "evaluate.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(evaluate_data, f, indent=2)

    compared = [r for r in all_rows if not r.get("gate")]
    if discrepancies:
        verdict = "discrepancy"
        reason = f"{len(discrepancies)} UI/JSON/API disagreements"
    elif not compared and hard_stop:
        verdict = "STOP"
        reason = "A hard stop ended the compare before UI, JSON, and API were read."
    elif not compared:
        verdict = "GATE"
        reason = "A storefront password gate stopped the read before UI, JSON, and API."
    else:
        verdict = "aligned"
        if any(r.get("gate") for r in all_rows):
            reason = "Compared rows match. One store stayed on the password gate and was not compared."
        else:
            reason = "UI price and availability match product JSON and products.json"
    protocol = {
        "timestamp": utc_str,
        "target": "H1-6 UI vs product JSON vs products.json API",
        "server_url": "http://127.0.0.1:8000/sse/?token=redacted",
        "source": "local-phantom+chrome",
        "sessions": 1,
        "verdict": verdict,
        "reason": reason,
        "results": [
            {
                "tool": f"{r.get('store')}:{r.get('handle')}",
                "status": "DISCREPANCY" if r.get("discrepancy") else str(r.get("status", "ok")).upper(),
                "latency_ms": r.get("latency_ms"),
                "details": (
                    f"ui={r.get('ui_price')} json={r.get('js_price')} api={r.get('api_price')} "
                    f"flags={r.get('flags')}"
                ),
            }
            for r in all_rows
        ],
    }
    with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2)

    md = [
        f"# H1-6 UI / JSON / API discrepancy matrix — {utc_str}",
        "",
        f"- **Stores**: A `{STORE_A}` · B `{STORE_B}`",
        f"- **Surfaces**: UI = PDP price · JSON = `/products/{{handle}}.js` · API = `/products.json`",
        f"- **Discrepancies**: `{len(discrepancies)}`",
        f"- **Verdict**: `{verdict}`",
        f"- **Gate A/B**: `{meta.get('A', {}).get('unlock')}` / `{meta.get('B', {}).get('unlock')}`",
        "- **Cart**: not cleared, not added, checkout not opened",
        "",
        "## Matrix",
        "",
        "| Store | Handle | UI | JSON | API | JSON available | API available | UI sold out | Flags | Status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in all_rows:
        md.append(
            f"| `{r.get('store')}` | `{r.get('handle')}` | {r.get('ui_price') or '-'} | "
            f"{r.get('js_price') or '-'} | {r.get('api_price') or '-'} | {r.get('js_available')} | "
            f"{r.get('api_available')} | {r.get('sold_out_text')} | "
            f"{','.join(r.get('flags') or []) or '-'} | **{r.get('status')}** |"
        )
    md.extend(["", "## Discrepancies", ""])
    if discrepancies:
        for r in discrepancies:
            md.append(
                f"- `{r['store']}:{r['handle']}` ui={r.get('ui_price')} json={r.get('js_price')} "
                f"api={r.get('api_price')} flags={r.get('flags')}"
            )
    else:
        if not compared:
            md.append("None compared. A storefront password gate stopped the read before UI, JSON, and API.")
        else:
            md.append("None. UI, product JSON, and products.json agree on price and availability.")
    md.append("")
    content = "\n".join(md)
    with open(os.path.join(run_dir, "MATRIX.md"), "w", encoding="utf-8") as f:
        f.write(content)
    with open(os.path.join(run_dir, "H1-6_full_product_matrix.md"), "w", encoding="utf-8") as f:
        f.write(content)
    with open(os.path.join(run_dir, "SMOKE.md"), "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] artifacts {run_dir} discrepancies={len(discrepancies)} hard_stop={hard_stop}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
