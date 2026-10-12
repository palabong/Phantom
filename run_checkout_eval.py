import os
import sys
import asyncio
import datetime
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_checkout_inspect"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
CART_URL = "https://xxxxxx-r48zg9i1.myshopify.com/cart"

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to Local Phantom: {SSE_URL}...")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Session initialized.")
            
            tool_calls = 0
            
            # --- Tool 1: Navigate directly to the cart ---
            print(f"\n[Tool 1/4] navigate -> {CART_URL}")
            await session.call_tool("navigate", {"url": CART_URL})
            tool_calls += 1
            
            # --- Tool 2: Execute form submission to proceed to checkout ---
            print("\n[Tool 2/4] evaluate -> Submit cart form / navigate to checkout")
            checkout_trigger_expr = """(() => {
                try {
                    // Try checkout button click first if present in DOM
                    const btn = document.querySelector('button[name="checkout"], input[name="checkout"], a[href*="/checkout"], .cart__checkout-button');
                    if (btn) {
                        btn.click();
                        return JSON.stringify({ method: 'btn_click', tag: btn.tagName, text: btn.innerText });
                    }
                    
                    // Fallback: submit cart form
                    const form = document.querySelector('form[action*="/cart"]');
                    if (form) {
                        form.submit();
                        return JSON.stringify({ method: 'form_submit' });
                    }
                    
                    // Fallback: direct navigation
                    location.href = '/checkout';
                    return JSON.stringify({ method: 'location_href' });
                } catch(e) {
                    location.href = '/checkout';
                    return JSON.stringify({ method: 'fallback_href', error: String(e) });
                }
            })()"""
            
            res_trigger = await session.call_tool("evaluate", {"expression": checkout_trigger_expr})
            tool_calls += 1
            print("Trigger Result:", res_trigger.content[0].text if res_trigger.content else "")
            
            # --- Tool 3: Wait for redirect to Shopify checkout boundary ---
            print("\n[Tool 3/4] wait -> 5000ms delay for checkout boundary redirect")
            await session.call_tool("wait", {"delay_ms": 5000})
            tool_calls += 1
            
            # --- Tool 4: Evaluate the checkout DOM ---
            print("\n[Tool 4/4] evaluate -> Extract checkout quantities, prices, error banners")
            eval_checkout_expr = """(() => {
                const href = location.href;
                const title = document.title;
                const bodyText = document.body ? document.body.innerText : "";
                
                // 1. Check for error banners, alerts, flash messages, inventory adjustment notices
                const notices = [];
                const noticeElements = Array.from(document.querySelectorAll(
                    '[role="alert"], [role="status"], .notice, .notice--error, .notice--warning, ' +
                    '.banner, .banner--critical, .banner--warning, .field__message--error, ' +
                    '[data-banner-id], [aria-live], .reduction-code-error'
                ));
                for (const el of noticeElements) {
                    const txt = el.innerText.trim();
                    if (txt && !notices.includes(txt)) {
                        notices.push(txt);
                    }
                }
                
                // Regex scan for stock/inventory warning keywords
                const stockWarningRegex = /(?:no longer available|out of stock|inventory|adjusted|reduced|limited to|maximum available|insufficient stock|non disponibile|esaurito)/i;
                const matchingLines = bodyText.split('\\n')
                    .map(l => l.trim())
                    .filter(l => l.length > 5 && stockWarningRegex.test(l));
                
                // 2. Extract line items & quantities from checkout DOM
                // Shopify checkout line items typically appear in [data-order-summary-section="line-items"] or table rows
                const lineItems = [];
                const itemRows = Array.from(document.querySelectorAll(
                    'tr.product, .product-table tr, [data-line-item], .order-summary__section__content tr'
                ));
                
                for (const row of itemRows) {
                    const txt = row.innerText.trim();
                    if (!txt) continue;
                    const titleEl = row.querySelector('.product__description__name, .product__description, th, .product-title');
                    const qtyEl = row.querySelector('.product-thumbnail__quantity, .product__quantity, [data-checkout-subtotal-item-quantity]');
                    const priceEl = row.querySelector('.product__price, .order-summary__emphasis, [data-checkout-line-item-price]');
                    
                    lineItems.push({
                        text: txt.replace(/\\n+/g, ' | '),
                        title: titleEl ? titleEl.innerText.trim() : null,
                        quantity: qtyEl ? qtyEl.innerText.trim() : null,
                        price: priceEl ? priceEl.innerText.trim() : null
                    });
                }
                
                // Specific extraction for "Beanie - Green" quantity
                let beanieQuantity = null;
                // Method A: from thumbnail quantity badge
                const beanieThumbQty = document.querySelector('.product[data-product-type*="Beanie"] .product-thumbnail__quantity, tr:has([alt*="Beanie"]) .product-thumbnail__quantity');
                if (beanieThumbQty) beanieQuantity = beanieThumbQty.innerText.trim();
                
                // Method B: Regex extraction from bodyText
                if (!beanieQuantity) {
                    const mQty = bodyText.match(/Beanie(?:\\s*-\\s*Green)?[\\s\\S]{0,100}?(?:qty|quantity)?[\\s:]*(\\d+)/i) ||
                                 bodyText.match(/(\\d+)\\s*(?:×|x)\\s*Beanie/i) ||
                                 bodyText.match(/Beanie[\\s\\S]{0,100}?\\$100\\.00[\\s\\S]{0,50}?(\\d+)/i);
                    if (mQty) beanieQuantity = mQty[1];
                }
                
                // 3. Extract total order price
                let totalPrice = null;
                const totalEl = document.querySelector('.total-line__price .payment-due__price, [data-checkout-payment-due-target], .payment-due__price');
                if (totalEl) {
                    totalPrice = totalEl.innerText.trim();
                } else {
                    const mTotal = bodyText.match(/(?:Total|Totale|Payment due)[\\s:]*([$€£\\d,.]+)/i);
                    if (mTotal) totalPrice = mTotal[1];
                }
                
                return JSON.stringify({
                    href: href,
                    title: title,
                    isCheckoutPage: href.includes('/checkouts/') || href.includes('/checkout') || title.toLowerCase().includes('checkout'),
                    beanieRequestedQuantity: beanieQuantity,
                    totalOrderPrice: totalPrice,
                    explicitNotices: notices,
                    inventoryMatchingLines: matchingLines,
                    detectedLineItems: lineItems,
                    bodySnippet: bodyText.slice(0, 1500)
                });
            })()"""
            
            res_eval = await session.call_tool("evaluate", {"expression": eval_checkout_expr})
            tool_calls += 1
            raw_eval = res_eval.content[0].text if res_eval.content else "{}"
            parsed = json.loads(raw_eval)
            if isinstance(parsed, str):
                try:
                    parsed = json.loads(parsed)
                except Exception:
                    pass
            print("\nCheckout Evaluation Data:")
            print(json.dumps(parsed, indent=2))
            
            print(f"\nTotal MCP Tool Calls Used: {tool_calls} / 4 permitted")
            
            # Archive artifact
            out_file = os.path.join(run_dir, "checkout_evaluation_outcome.json")
            with open(out_file, "w") as f:
                json.dump(parsed, f, indent=2)
            print(f"Saved artifact to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
