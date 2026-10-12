import os
import sys
import time
import asyncio
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

TOKEN = "ph_live_beanie_admin_check"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"
ADMIN_URL = "https://admin.shopify.com/store/xxxxxx-r48zg9i1/products?query=beanie"

async def main():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_now}"
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Connecting to Local Phantom via SSE: {SSE_URL}...")
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Session initialized.")
            
            # 1. get_snapshot html (confirm still authenticated as H1 Staff)
            print("\n--- Step 1: get_snapshot html ---")
            snap1 = await session.call_tool("get_snapshot", {"mode": "html"})
            snap1_text = snap1.content[0].text if snap1.content else ""
            print(f"Step 1 snapshot length: {len(snap1_text)} chars")
            has_h1_staff_1 = "h1 staff" in snap1_text.lower() or "palabong" in snap1_text.lower()
            print(f"H1 Staff present in step 1 snapshot: {has_h1_staff_1}")
            
            # Save step 1 snapshot
            with open(os.path.join(run_dir, "snapshot_step1.txt"), "w") as f:
                f.write(snap1_text)
                
            # 2. One navigate only to: https://admin.shopify.com/store/xxxxxx-r48zg9i1/products?query=beanie
            print(f"\n--- Step 2: One navigate only to: {ADMIN_URL} ---")
            nav_res = await session.call_tool("navigate", {"url": ADMIN_URL})
            nav_text = nav_res.content[0].text if nav_res.content else ""
            print(f"Navigation result: {nav_text}")
            
            # Wait for hydration
            await session.call_tool("wait", {"delay_ms": 3000})
            
            # 3. get_snapshot html on the result
            print("\n--- Step 3: get_snapshot html on the result ---")
            snap3 = await session.call_tool("get_snapshot", {"mode": "html"})
            snap3_text = snap3.content[0].text if snap3.content else ""
            print(f"Step 3 snapshot length: {len(snap3_text)} chars")
            has_h1_staff_3 = "h1 staff" in snap3_text.lower() or "palabong" in snap3_text.lower()
            print(f"H1 Staff present in step 3 snapshot: {has_h1_staff_3}")
            
            with open(os.path.join(run_dir, "snapshot_step3.txt"), "w") as f:
                f.write(snap3_text)
                
            # 4. evaluate: extract the inventory text for Beanie (e.g. "X in stock for Y variants") and any available/sellable status
            print("\n--- Step 4: evaluate product info ---")
            eval_expr = """(() => {
                const title = document.title;
                const href = location.href;
                const bodyText = document.body ? document.body.innerText : "";
                
                // Check if challenged or on login page
                const isChallenge = /challenge|turnstile|recaptcha|just a moment/i.test(title + " " + bodyText);
                const isLogin = /login|accounts\.shopify\.com/i.test(href);
                
                // Extract table rows / polaris items
                const rows = Array.from(document.querySelectorAll('tr, [role="row"], .Polaris-IndexTable__TableRow'));
                let beanieRowText = null;
                let beanieInventory = null;
                let beanieStatus = null;
                
                for (const row of rows) {
                    const text = row.innerText;
                    if (/beanie/i.test(text)) {
                        beanieRowText = text;
                        // look for "X in stock"
                        const mStock = text.match(/(\\d+\\s+in\\s+stock(?:\\s+for\\s+\\d+\\s+variants)?)/i);
                        if (mStock) beanieInventory = mStock[1];
                        
                        const mStatus = text.match(/\\b(Active|Draft|Archived)\\b/i);
                        if (mStatus) beanieStatus = mStatus[1];
                        break;
                    }
                }
                
                // Fallback: search body text
                if (!beanieInventory) {
                    const mStock2 = bodyText.match(/Beanie[\\s\\S]{0,200}?(\\d+\\s+in\\s+stock(?:\\s+for\\s+\\d+\\s+variants)?)/i);
                    if (mStock2) beanieInventory = mStock2[1];
                }
                if (!beanieStatus) {
                    const mStatus2 = bodyText.match(/Beanie[\\s\\S]{0,200}?\\b(Active|Draft|Archived)\\b/i);
                    if (mStatus2) beanieStatus = mStatus2[1];
                }
                
                // Check staff authentication in header/account menu
                const staffDetected = /H1 Staff|palabong\\+staff/i.test(bodyText);
                
                return JSON.stringify({
                    href: href,
                    title: title,
                    isChallenge: isChallenge,
                    isLogin: isLogin,
                    staffDetected: staffDetected,
                    beanieFound: !!beanieRowText || !!beanieInventory,
                    beanieRowText: beanieRowText,
                    beanieInventory: beanieInventory,
                    beanieStatus: beanieStatus,
                    bodyPreview: bodyText.slice(0, 1000)
                });
            })()"""
            
            eval_res = await session.call_tool("evaluate", {"expression": eval_expr})
            raw_eval = eval_res.content[0].text if eval_res.content else "{}"
            parsed_eval = json.loads(raw_eval)
            if isinstance(parsed_eval, str):
                try:
                    parsed_eval = json.loads(parsed_eval)
                except Exception:
                    pass
            print("Evaluation Result:", json.dumps(parsed_eval, indent=2))
            
            # 5. Write outcome from evaluate only. Stop.
            outcome_lines = [
                "# Beanie Admin Inventory & Status Evaluation",
                f"- **Timestamp (UTC)**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                f"- **Target URL**: `{ADMIN_URL}`",
                f"- **Current URL**: `{parsed_eval.get('href')}`",
                f"- **Page Title**: `{parsed_eval.get('title')}`",
                f"- **Staff Authenticated**: {parsed_eval.get('staffDetected')}",
                f"- **Login Page Redirect**: {parsed_eval.get('isLogin')}",
                f"- **Bot Challenge Detected**: {parsed_eval.get('isChallenge')}",
                "",
                "## Extracted Evaluation Data",
                f"- **Product Title**: Beanie",
                f"- **Inventory**: {parsed_eval.get('beanieInventory') or 'Not Found / Not Visible'}",
                f"- **Status (Available / Sellable)**: {parsed_eval.get('beanieStatus') or 'Not Found / Not Visible'}",
                f"- **Row Text**: `{parsed_eval.get('beanieRowText')}`",
                "",
                "## Page Context Preview",
                "```text",
                f"{parsed_eval.get('bodyPreview', '')[:600]}",
                "```"
            ]
            
            out_file = os.path.join(run_dir, "beanie_admin_inventory_outcome.md")
            with open(out_file, "w") as f:
                f.write("\n".join(outcome_lines))
            print(f"\n[DONE] Outcome written to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
