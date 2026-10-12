import asyncio
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8000/sse/?token=ph_live_D2aZuYtdGL6tUfuV2egoxp"

TARGET_URLS = [
    ("home", "https://admin.shopify.com/store/funk-it-up-sdzgxmea"),
    ("settings", "https://admin.shopify.com/store/funk-it-up-sdzgxmea/settings"),
    ("themes", "https://admin.shopify.com/store/funk-it-up-sdzgxmea/themes")
]

async def run():
    results = {}
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] Session initialized.")

            for label, url in TARGET_URLS:
                print(f"\n--- Testing Staff: {label} -> {url} ---")
                nav_res = await session.call_tool("navigate", {"url": url})
                print("Nav res:", nav_res.content[0].text if nav_res.content else "")
                await session.call_tool("wait", {"delay_ms": 4000})

                eval_expr = r"""(() => {
                    const title = document.title || "";
                    const href = location.href || "";
                    const bodyText = document.body ? document.body.innerText : "";
                    
                    // Check for deny banner or permission denied
                    const isDenied = /permission|non hai i permessi|access denied|not authorized|denied/i.test(bodyText) ||
                                     /ci siamo quasi|just a moment/i.test(title) ||
                                     (title === "Shopify" && !/home|prodotti|products|impostazioni|settings|temi|themes/i.test(bodyText.slice(0, 500)));
                                     
                    return JSON.stringify({
                        href: href,
                        title: title,
                        denied: isDenied,
                        bodyPreview: bodyText.slice(0, 300).replace(/\n+/g, ' ')
                    });
                })()"""

                res = await session.call_tool("evaluate", {"expression": eval_expr})
                raw = res.content[0].text if res.content else "{}"
                data = json.loads(raw)
                if isinstance(data, str):
                    data = json.loads(data)
                print(f"[+] Result for {label}:", json.dumps(data, indent=2))
                results[label] = data

    with open("staff_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

asyncio.run(run())
