import asyncio
import json
import os
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8000/sse/?token=ph_live_D2aZuYtdGL6tUfuV2egoxp"
TARGET_URL = "https://admin.shopify.com/store/funk-it-up-sdzgxmea/products/10323603521722"

async def run():
    print(f"[*] Connecting to local Phantom SSE server: {SSE_URL}")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] Session initialized.")

            # Step 1: Pre-check snapshot
            print("\n--- Step 1: Preflight get_snapshot html ---")
            snap1 = await session.call_tool("get_snapshot", {"mode": "html"})
            snap1_text = snap1.content[0].text if snap1.content else ""
            print(f"[+] Snapshot 1 len: {len(snap1_text)}")

            # Step 2: Navigate to product 10323603521722
            print(f"\n--- Step 2: Navigate to {TARGET_URL} ---")
            nav_res = await session.call_tool("navigate", {"url": TARGET_URL})
            nav_text = nav_res.content[0].text if nav_res.content else ""
            print(f"[+] Navigate output: {nav_text}")

            print("[*] Waiting 4500ms for Polaris UI hydration...")
            await session.call_tool("wait", {"delay_ms": 4500})

            # Step 3: get_snapshot html
            print("\n--- Step 3: get_snapshot html ---")
            snap2 = await session.call_tool("get_snapshot", {"mode": "html"})
            snap2_text = snap2.content[0].text if snap2.content else ""
            print(f"[+] Snapshot 2 len: {len(snap2_text)}")

            # Check if challenge/captcha appeared
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", snap2_text, re.I):
                print("[!] Cloudflare/captcha challenge detected! Writing STOP.txt...")
                with open("STOP.txt", "w", encoding="utf-8") as f:
                    f.write("Cloudflare or captcha\n")
                return

            # Step 4: evaluate to read DOM
            print("\n--- Step 4: evaluate DOM ---")
            eval_js = r"""(() => {
                const titleElem = document.querySelector('h1, input[name="title"], [data-polaris-header-title="true"]');
                const title = titleElem ? (titleElem.value || titleElem.innerText || "").trim() : (document.title || "");
                
                // Status (Active, Draft, Archived)
                let status = "Unknown";
                const statusSelect = document.querySelector('select[name="status"], [data-testid="product-status"]');
                if (statusSelect) {
                    status = statusSelect.value || statusSelect.innerText || "";
                } else {
                    const statusBadge = document.querySelector('.Polaris-Badge, [class*="Badge"]');
                    if (statusBadge) status = statusBadge.innerText.trim();
                }
                
                // Published state / Publishing channels
                const publishingCards = Array.from(document.querySelectorAll('[class*="Card"], [class*="LegacyCard"], [role="region"], section')).filter(el => {
                    const t = el.innerText || "";
                    return t.includes("Publishing") || t.includes("Sales channels") || t.includes("Markets") || t.includes("Online Store");
                }).map(el => el.innerText.trim());
                
                // Price & Inventory & Variants
                const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
                    name: i.name,
                    id: i.id,
                    type: i.type,
                    value: i.value,
                    placeholder: i.placeholder
                }));
                
                const rows = Array.from(document.querySelectorAll('tr, [role="row"], .Polaris-IndexTable__TableRow'));
                const variants = [];
                for (const r of rows) {
                    const text = (r.innerText || "").trim().replace(/\n+/g, ' | ');
                    if (!text) continue;
                    // look for variant link or id
                    const link = r.querySelector('a[href*="/variants/"]');
                    const href = link ? link.getAttribute('href') : "";
                    const m = href.match(/\/variants\/(\d+)/);
                    const vid = m ? m[1] : null;
                    variants.push({
                        text: text,
                        variantId: vid,
                        href: href
                    });
                }
                
                // Also search all variant links on page
                const allVariantLinks = Array.from(document.querySelectorAll('a[href*="/variants/"]')).map(a => ({
                    href: a.getAttribute('href'),
                    text: a.innerText.trim()
                }));
                
                // Error / warning banners or UI deny
                const banners = Array.from(document.querySelectorAll('[role="alert"], .Polaris-Banner')).map(b => b.innerText.trim());
                
                // Check visible nav items (Settings, Orders, etc.)
                const navLinks = Array.from(document.querySelectorAll('nav a, [role="navigation"] a')).map(a => a.innerText.trim());

                return JSON.stringify({
                    href: location.href,
                    documentTitle: document.title,
                    productTitle: title,
                    status: status,
                    publishingCards: publishingCards,
                    variants: variants,
                    allVariantLinks: allVariantLinks,
                    banners: banners,
                    navLinks: navLinks,
                    bodySnippet: document.body ? document.body.innerText.slice(0, 3000) : ""
                });
            })()"""

            eval_res = await session.call_tool("evaluate", {"expression": eval_js})
            raw_eval = eval_res.content[0].text if eval_res.content else "{}"
            data = json.loads(raw_eval)
            if isinstance(data, str):
                data = json.loads(data)

            print("[+] EVALUATION RESULT:")
            print(json.dumps(data, indent=2))

            with open("product_a_eval.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

asyncio.run(run())
