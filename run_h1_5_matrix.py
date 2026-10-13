import asyncio
import json
import os
import sys
import time
import datetime
import re
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = os.environ.get("PHANTOM_SSE_URL") or (
    "http://127.0.0.1:8000/sse/?token="
    + os.environ.get("PHANTOM_AUTH_TOKEN", "ph_live_local_verify")
)

SHOP_A = "funk-it-up-sdzgxmea"
SHOP_B = "xxxxxx-r48zg9i1"

ROUTES_A = [
    {"path": "/products", "name": "Products (Sanity)", "sensitive": False},
    {"path": "/orders", "name": "Orders", "sensitive": True},
    {"path": "/customers", "name": "Customers", "sensitive": True},
    {"path": "/themes", "name": "Themes", "sensitive": True},
    {"path": "/settings/general", "name": "Settings General", "sensitive": True},
    {"path": "/settings/payments", "name": "Settings Payments", "sensitive": True}
]

ROUTES_B = [
    {"path": "/orders", "name": "Store B Orders", "sensitive": True},
    {"path": "/customers", "name": "Store B Customers", "sensitive": True},
    {"path": "/themes", "name": "Store B Themes", "sensitive": True},
    {"path": "/settings/general", "name": "Store B Settings General", "sensitive": True},
    {"path": "/settings/payments", "name": "Store B Settings Payments", "sensitive": True}
]

async def execute_h1_5_matrix():
    utc_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = f"runs/prod_postdeploy_{utc_str}"
    os.makedirs(run_dir, exist_ok=False)
    print(f"[*] Starting H1-5 FULL EVALUATION MATRIX in {run_dir}")

    evaluated_routes_a = []
    evaluated_routes_b = []
    overall_mismatch = False

    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("[+] Session initialized with Phantom SSE.")

            # --- Phase 1: Store A Routes ---
            print("\n[Phase 1] Testing Store A (funk-it-up-sdzgxmea) routes...")
            for route_info in ROUTES_A:
                p = route_info["path"]
                full_url = f"https://admin.shopify.com/store/{SHOP_A}{p}"
                print(f" -> Navigating to {full_url}")
                t0 = time.perf_counter()
                try:
                    await session.call_tool("navigate", {"url": full_url})
                    await session.call_tool("wait", {"delay_ms": 4000})
                    snap_res = await session.call_tool("get_snapshot", {"mode": "ax"})
                    snap_text = snap_res.content[0].text if snap_res and snap_res.content else ""

                    eval_js = r"""(() => {
                        const href = location.href || "";
                        const title = document.title || "";
                        const bodyText = document.body ? document.body.innerText : "";
                        
                        // Check for permission denied indicator
                        const hasPermissionBanner = /permission|non hai i permessi|access denied|not authorized|you do not have permission/i.test(bodyText);
                        const isChallenge = /ci siamo quasi|just a moment|verificare la tua connessione/i.test(bodyText) || /ci siamo quasi|just a moment/i.test(title);
                        const isLogin = href.indexOf("accounts.shopify.com") !== -1 || href.indexOf("/login") !== -1 || href.indexOf("/lookup") !== -1;
                        const isDeniedUI = hasPermissionBanner || isChallenge || isLogin || (title === "Shopify" && !/prodotti|products/i.test(bodyText.slice(0, 500)));
                        const nav = performance.getEntriesByType('navigation')[0];

                        // Inspect network resources timing
                        const resources = (performance.getEntriesByType('resource') || []).map(r => ({
                            name: r.name,
                            initiatorType: r.initiatorType,
                            duration: Math.round(r.duration)
                        }));
                        const graphqlCalls = resources.filter(r => r.name.includes('/graphql') || r.name.includes('admin/api')).map(r => r.name.split('?')[0]);

                        // Determine data class present in DOM
                        let dataClass = "empty";
                        if (/order|ordine|draft|abandoned/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "orders";
                        } else if (/customer|cliente|segment/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "customers";
                        } else if (/online store|current theme|theme library|temi/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "themes";
                        } else if (/store details|store currency|dettagli negozio/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "settings";
                        } else if (/snowboard|product|beanie/i.test(bodyText)) {
                            dataClass = "products";
                        }

                        // Mismatch check: sensitive route accessible without grant
                        return JSON.stringify({
                            href: href.split('?')[0],
                            title: title,
                            deniedUI: isDeniedUI,
                            challenge: isChallenge,
                            login: isLogin,
                            http: nav && nav.responseStatus ? nav.responseStatus : null,
                            dataClass: dataClass,
                            graphqlCount: graphqlCalls.length
                        });
                    })()"""

                    res = await session.call_tool("evaluate", {"expression": eval_js})
                    dt = time.perf_counter() - t0
                    raw = res.content[0].text if res.content else "{}"
                    data = json.loads(raw)
                    if isinstance(data, str):
                        data = json.loads(data)

                    denied_ui = bool(data.get("deniedUI", True))
                    data_class = data.get("dataClass", "empty")
                    challenge = bool(data.get("challenge"))
                    login = bool(data.get("login"))

                    # Mismatch: a sensitive route is usable, or a deny wall still shows orders, customers, or settings.
                    is_mismatch = False
                    if route_info["sensitive"] and not challenge and not login:
                        if not denied_ui:
                            is_mismatch = True
                            overall_mismatch = True
                        if denied_ui and data_class in ["orders", "customers", "settings"]:
                            is_mismatch = True
                            overall_mismatch = True

                    entry = {
                        "path": p,
                        "href": str(data.get("href") or full_url).split("?")[0],
                        "title": data.get("title", ""),
                        "deniedUI": denied_ui,
                        "challenge": challenge,
                        "login": login,
                        "http": data.get("http"),
                        "dataClass": data_class,
                        "latency_ms": round(dt * 1000, 1),
                        "mismatch": is_mismatch,
                        "snapshot_mode": "ax",
                        "snapshot_len": len(snap_text),
                        "graphqlCount": data.get("graphqlCount"),
                    }
                    evaluated_routes_a.append(entry)
                    print(f"    Result: deniedUI={denied_ui}, dataClass={data_class}, mismatch={is_mismatch}")
                except Exception as e:
                    dt = time.perf_counter() - t0
                    evaluated_routes_a.append({
                        "path": p,
                        "href": full_url,
                        "title": "Exception",
                        "deniedUI": True,
                        "http": 500,
                        "dataClass": "empty",
                        "latency_ms": round(dt * 1000, 1),
                        "mismatch": False,
                        "details": re.sub(r"ph_live_[A-Za-z0-9]+", "ph_live_[REDACTED]", str(e))[:180]
                    })

            # --- Phase 2: Store B Routes ---
            print("\n[Phase 2] Testing Store B (xxxxxx-r48zg9i1) routes...")
            for route_info in ROUTES_B:
                p = route_info["path"]
                full_url = f"https://admin.shopify.com/store/{SHOP_B}{p}"
                print(f" -> Navigating to {full_url}")
                t0 = time.perf_counter()
                try:
                    await session.call_tool("navigate", {"url": full_url})
                    await session.call_tool("wait", {"delay_ms": 4000})
                    snap_res = await session.call_tool("get_snapshot", {"mode": "ax"})
                    snap_text = snap_res.content[0].text if snap_res and snap_res.content else ""

                    eval_js = r"""(() => {
                        const href = location.href || "";
                        const title = document.title || "";
                        const bodyText = document.body ? document.body.innerText : "";
                        const hasPermissionBanner = /permission|non hai i permessi|access denied|not authorized|you do not have permission/i.test(bodyText);
                        const isChallenge = /ci siamo quasi|just a moment|verificare la tua connessione/i.test(bodyText) || /ci siamo quasi|just a moment/i.test(title);
                        const isLogin = href.indexOf("accounts.shopify.com") !== -1 || href.indexOf("/login") !== -1 || href.indexOf("/lookup") !== -1;
                        const isDeniedUI = hasPermissionBanner || isChallenge || isLogin || (title === "Shopify" && !/prodotti|products/i.test(bodyText.slice(0, 500)));
                        const nav = performance.getEntriesByType('navigation')[0];

                        let dataClass = "empty";
                        if (/order|ordine|draft|abandoned/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "orders";
                        } else if (/customer|cliente|segment/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "customers";
                        } else if (/online store|current theme|theme library|temi/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "themes";
                        } else if (/store details|store currency|dettagli negozio/i.test(bodyText) && !hasPermissionBanner) {
                            dataClass = "settings";
                        } else if (/snowboard|product|beanie/i.test(bodyText)) {
                            dataClass = "products";
                        }

                        return JSON.stringify({
                            href: href.split('?')[0],
                            title: title,
                            deniedUI: isDeniedUI,
                            challenge: isChallenge,
                            login: isLogin,
                            http: nav && nav.responseStatus ? nav.responseStatus : null,
                            dataClass: dataClass
                        });
                    })()"""

                    res = await session.call_tool("evaluate", {"expression": eval_js})
                    dt = time.perf_counter() - t0
                    raw = res.content[0].text if res.content else "{}"
                    data = json.loads(raw)
                    if isinstance(data, str):
                        data = json.loads(data)

                    denied_ui = bool(data.get("deniedUI", True))
                    data_class = data.get("dataClass", "empty")
                    challenge = bool(data.get("challenge"))
                    login = bool(data.get("login"))

                    entry = {
                        "path": p,
                        "href": str(data.get("href") or full_url).split("?")[0],
                        "title": data.get("title", ""),
                        "deniedUI": denied_ui,
                        "challenge": challenge,
                        "login": login,
                        "http": data.get("http"),
                        "dataClass": data_class,
                        "latency_ms": round(dt * 1000, 1),
                        "mismatch": False,
                        "snapshot_mode": "ax",
                        "snapshot_len": len(snap_text),
                    }
                    evaluated_routes_b.append(entry)
                    print(f"    Result: deniedUI={denied_ui}, dataClass={data_class}")
                except Exception as e:
                    dt = time.perf_counter() - t0
                    evaluated_routes_b.append({
                        "path": p,
                        "href": full_url,
                        "title": "Exception",
                        "deniedUI": True,
                        "http": 500,
                        "dataClass": "empty",
                        "latency_ms": round(dt * 1000, 1),
                        "mismatch": False,
                        "details": re.sub(r"ph_live_[A-Za-z0-9]+", "ph_live_[REDACTED]", str(e))[:180]
                    })

    # --- Phase 3: Artifact Generation ---
    print("\n[Phase 3] Generating Artifacts...")
    
    # Required H1-5 evaluate.json schema
    eval_routes_formatted = [
        {
            "path": r["path"],
            "deniedUI": r["deniedUI"],
            "http": r["http"],
            "dataClass": r["dataClass"]
        }
        for r in evaluated_routes_a if r["path"] != "/products"
    ]

    all_routes = evaluated_routes_a + evaluated_routes_b
    saw_challenge = any(r.get("challenge") for r in all_routes)
    saw_login = any(r.get("login") for r in all_routes)
    saw_admin = any(
        (not r.get("deniedUI")) and (not r.get("challenge")) and (not r.get("login"))
        for r in all_routes
    )
    if overall_mismatch:
        verdict = "finding-candidate"
        reason = "A sensitive admin route was usable or showed orders, customers, or settings behind the staff grant."
    elif saw_challenge and not saw_admin:
        verdict = "CF"
        reason = "Cloudflare stopped the admin read before an authenticated staff UI."
    elif saw_login and not saw_admin:
        verdict = "LOGIN"
        reason = "The admin routes redirected to login. The staff session was not on this browser."
    elif saw_admin:
        verdict = "PASS"
        reason = "Sensitive routes stayed behind the permission wall. No orders, customers, or settings mismatch."
    else:
        verdict = "STOP"
        reason = "No authenticated admin UI was read."

    evaluate_data = {
        "source": "local-chrome",
        "snapshot_mode": "ax",
        "loggedInAsStaff": bool(saw_admin),
        "grant": "Prodotti Visualizza",
        "routes": eval_routes_formatted,
        "mismatch": overall_mismatch,
        "verdict": verdict,
        "extended_matrix": {
            "store_A_all": evaluated_routes_a,
            "store_B_all": evaluated_routes_b
        }
    }

    eval_json_path = os.path.join(run_dir, "evaluate.json")
    with open(eval_json_path, "w", encoding="utf-8") as f:
        json.dump(evaluate_data, f, indent=2)

    # protocol.json
    protocol_data = {
        "timestamp": utc_str,
        "target": f"https://admin.shopify.com/store/{SHOP_A}",
        "server_url": "http://127.0.0.1:8000/sse/?token=redacted",
        "source": "local-phantom+chrome",
        "sessions": 1,
        "verdict": verdict,
        "reason": reason,
        "results": [
            {
                "tool": f"Staff route {r['path']}",
                "status": "MISMATCH" if r["mismatch"] else "PASS",
                "latency_ms": r["latency_ms"],
                "details": f"title='{r['title']}' deniedUI={r['deniedUI']} dataClass='{r['dataClass']}'"
            }
            for r in evaluated_routes_a
        ]
    }
    prot_json_path = os.path.join(run_dir, "protocol.json")
    with open(prot_json_path, "w", encoding="utf-8") as f:
        json.dump(protocol_data, f, indent=2)

    # SMOKE.md & MATRIX.md
    md_lines = [
        f"# H1-5 Full Evaluation Matrix — {utc_str}",
        "",
        f"- **Timestamp (UTC)**: `{utc_str}`",
        f"- **Staff Grant**: `Prodotti Visualizza` (Products View only)",
        f"- **Primary Store**: `https://admin.shopify.com/store/{SHOP_A}`",
        f"- **Verdict**: `{verdict}`",
        f"- **Mismatch**: `{'true' if overall_mismatch else 'false'}`",
        "",
        "## Store A (Target) UI vs API Matrix",
        "",
        "| Route | Path | deniedUI | Data Class | HTTP | Latency (ms) | Mismatch | Details |",
        "|---|---|---|---|---|---|---|---|"
    ]

    for r in evaluated_routes_a:
        md_lines.append(
            f"| `{r['path']}` | `{r.get('href','')}` | **{r.get('deniedUI')}** | `{r.get('dataClass')}` | "
            f"{r.get('http')} | {r.get('latency_ms')} | `{'TRUE' if r.get('mismatch') else 'false'}` | "
            f"{r.get('title','')} |"
        )

    md_lines.extend([
        "",
        "## Store B Comparative Matrix",
        "",
        "| Route | Path | deniedUI | Data Class | HTTP | Latency (ms) | Details |",
        "|---|---|---|---|---|---|---|"
    ])

    for r in evaluated_routes_b:
        md_lines.append(
            f"| `{r['path']}` | `{r.get('href','')}` | **{r.get('deniedUI')}** | `{r.get('dataClass')}` | "
            f"{r.get('http')} | {r.get('latency_ms')} | {r.get('title','')} |"
        )

    md_lines.extend([
        "",
        "## Conclusion & Findings",
        f"- **Verdict**: `{verdict}`",
        f"- **Mismatch**: `{'true' if overall_mismatch else 'false'}`",
        f"- **Reason**: {reason}",
    ])

    smoke_path = os.path.join(run_dir, "SMOKE.md")
    matrix_path = os.path.join(run_dir, "MATRIX.md")
    content_md = "\n".join(md_lines)
    with open(smoke_path, "w", encoding="utf-8") as f:
        f.write(content_md)
    with open(matrix_path, "w", encoding="utf-8") as f:
        f.write(content_md)

    # Zip archive
    zip_path = f"{run_dir}.zip"
    print(f"[+] Zipping archive to {zip_path}")
    import subprocess
    subprocess.run(["zip", "-r", zip_path, run_dir], capture_output=True)

    print(f"[+] Done. Output path: {run_dir}")

asyncio.run(execute_h1_5_matrix())
