import asyncio
import os
import sys
import time
import datetime
import json
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

CONFIG_PATH = os.path.join(".agents", "mcp_config.json")
TOKEN = "ph_live_D2aZuYtdGL6tUfuV2egoxp"
SSE_URL = f"http://127.0.0.1:8000/sse/?token={TOKEN}"

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            url = cfg.get("mcpServers", {}).get("phantom-cloud-local", {}).get("serverUrl")
            if url:
                SSE_URL = url
    except Exception as e:
        print(f"Warning loading mcp_config.json: {e}")

TARGET_NAV_URL = "https://admin.shopify.com/store/xxxxxx-r48zg9i1/settings/payments"
EVAL_EXPR = "return await fetch('https://xxxxxx-r48zg9i1.myshopify.com/admin/api/2024-10/graphql.json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:'query{shop{paymentSettings{supportedDigitalWallets}}}'})}).then(r=>r.json()).then(d=>JSON.stringify(d)).catch(e=>JSON.stringify({error:e.message}));"

async def run():
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join("runs", f"prod_postdeploy_{utc_timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    print(f"[*] Archive directory: {run_dir}")
    print(f"[*] Connecting to {SSE_URL} (single session)...")

    protocol_log = []

    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] MCP Session successfully initialized.")

            # --- Step 1: navigate to settings/payments URL ---
            print(f"\n--- [Step 1] navigate to {TARGET_NAV_URL} ---")
            t0 = time.perf_counter()
            nav_res = await session.call_tool("navigate", {"url": TARGET_NAV_URL})
            dt_nav = (time.perf_counter() - t0) * 1000
            nav_text = nav_res.content[0].text if nav_res.content else ""
            print(f"[+] Navigation completed in {dt_nav:.1f}ms: {nav_text}")

            protocol_log.append({
                "step": "step1_navigate",
                "url": TARGET_NAV_URL,
                "duration_ms": dt_nav,
                "result": nav_text
            })

            # Wait for Polaris UI hydration
            print("[*] Waiting 3000ms for Polaris UI hydration...")
            await session.call_tool("wait", {"delay_ms": 3000})

            # --- Step 2: get_snapshot html ---
            print("\n--- [Step 2] get_snapshot html ---")
            t0 = time.perf_counter()
            snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
            dt_snap = (time.perf_counter() - t0) * 1000
            snap_text = snap_res.content[0].text if snap_res.content else ""
            print(f"[+] Snapshot retrieved in {dt_snap:.1f}ms ({len(snap_text)} characters).")

            with open(os.path.join(run_dir, "snapshot_payments.html"), "w", encoding="utf-8") as f:
                f.write(snap_text)

            protocol_log.append({
                "step": "step2_get_snapshot",
                "duration_ms": dt_snap,
                "length": len(snap_text),
                "preview": snap_text[:300]
            })

            # If Turnstile already resolved successfully and is handing over, wait for redirect
            if re.search(r"verifica riuscita|verification successful", snap_text, re.I):
                print("[*] Turnstile verification passed, waiting 3000ms for redirect to complete...")
                await session.call_tool("wait", {"delay_ms": 3000})
                snap_res = await session.call_tool("get_snapshot", {"mode": "html"})
                snap_text = snap_res.content[0].text if snap_res.content else ""
                with open(os.path.join(run_dir, "snapshot_payments.html"), "w", encoding="utf-8") as f:
                    f.write(snap_text)
                protocol_log.append({
                    "step": "step2_get_snapshot_post_handover",
                    "length": len(snap_text),
                    "preview": snap_text[:300]
                })

            # Check for challenge or captcha
            if re.search(r"challenge|turnstile|recaptcha|just a moment|ci siamo quasi", snap_text, re.I):
                print("[!] Challenge or captcha present. Stopping.")
                stop_msg = "challenge or captcha present\n"
                with open(os.path.join(run_dir, "STOP.txt"), "w", encoding="utf-8") as f:
                    f.write(stop_msg)
                with open("STOP.txt", "w", encoding="utf-8") as f:
                    f.write(stop_msg)
                with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                    json.dump(protocol_log, f, indent=2)
                return

            # Analyze snapshot: permission denial vs payments content
            snap_lower = snap_text.lower()
            is_permission_denial = bool(
                re.search(r"you need permission|doesn't have access|non hai i permessi|access denied|accesso negato|not authorized|non autorizzato|request access", snap_lower)
            )
            has_payments_content = bool(
                re.search(r"payment providers|payment methods|supported payment|shopify payments|third-party providers|pagamenti|provider di pagamento|manual payment", snap_lower)
            )

            if is_permission_denial and not has_payments_content:
                ui_state = "permission denial"
                m = re.search(r"([^\.\n]*?(?:permission|access)[^\.\n]*?\.)", snap_text, re.I)
                ui_detail = m.group(1).strip() if m else "permission denied to view payments"
            elif has_payments_content:
                ui_state = "payments content"
                ui_detail = "payments configuration and providers displayed"
            elif is_permission_denial:
                ui_state = "permission denial"
                ui_detail = "permission denied to view payments"
            else:
                ui_state = "payments content"
                ui_detail = "payments settings page rendered"

            print(f"[+] UI Observation: {ui_state} ({ui_detail})")

            # --- Step 3: evaluate GraphQL payment query ---
            print(f"\n--- [Step 3] evaluate GraphQL payment query ---")
            t0 = time.perf_counter()
            eval_res = await session.call_tool("evaluate", {"expression": EVAL_EXPR})
            dt_eval = (time.perf_counter() - t0) * 1000
            eval_raw = eval_res.content[0].text if eval_res.content else ""
            print(f"[+] Evaluate returned in {dt_eval:.1f}ms: {eval_raw}")

            protocol_log.append({
                "step": "step3_evaluate",
                "expression": EVAL_EXPR,
                "duration_ms": dt_eval,
                "result": eval_raw
            })

            eval_json_str = eval_raw
            try:
                parsed = json.loads(eval_raw)
                if isinstance(parsed, str):
                    try:
                        parsed = json.loads(parsed)
                        eval_json_str = json.dumps(parsed, ensure_ascii=False)
                    except Exception:
                        eval_json_str = parsed
                else:
                    eval_json_str = json.dumps(parsed, ensure_ascii=False)
            except Exception:
                pass

            with open(os.path.join(run_dir, "evaluate.json"), "w", encoding="utf-8") as f:
                f.write(eval_json_str)

            # --- Step 4: Write result.txt with the UI observation and the evaluate JSON. Stop. ---
            print("\n--- [Step 4] Writing result.txt ---")
            result_content = f"UI observation: {ui_state} ({ui_detail})\nEvaluate JSON: {eval_json_str}\n"

            result_file_run = os.path.join(run_dir, "result.txt")
            with open(result_file_run, "w", encoding="utf-8") as f:
                f.write(result_content)

            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(result_content)

            with open(os.path.join(run_dir, "protocol.json"), "w", encoding="utf-8") as f:
                json.dump(protocol_log, f, indent=2)

            if os.path.exists("STOP.txt"):
                try:
                    os.remove("STOP.txt")
                except Exception:
                    pass

            print(f"[+] result.txt written to {result_file_run} and result.txt")
            print(f"[+] Output:\n{result_content.strip()}")
            print(f"[+] Finished run archive: {run_dir}")

if __name__ == "__main__":
    asyncio.run(run())
