import asyncio
import os
import json
import time

# Import the phantom cloud module functions directly
import phantom_cloud

async def run_test():
    print("Initializing test sequence on local phantom_cloud engine...", flush=True)
    
    # Set Unkey root key to None in memory to bypass token auth during direct function calls
    phantom_cloud.UNKEY_ROOT_KEY = None
    
    try:
        # 1. Execute 'navigate' tool on sannysoft
        target_url = "https://bot.sannysoft.com/"
        print(f"\n[1/2] Invoking 'navigate' tool against: {target_url}", flush=True)
        start_time = time.time()
        
        # We invoke handle_call_tool directly
        res_nav = await phantom_cloud.handle_call_tool("navigate", {"url": target_url})
        nav_duration = time.time() - start_time
        print(f"Status: {res_nav[0].text}")
        print(f"Navigation took: {nav_duration:.2f} seconds")
        
        # 2. Execute 'get_snapshot' tool
        print("\n[2/2] Invoking 'get_snapshot' tool...", flush=True)
        start_time = time.time()
        res_snap = await phantom_cloud.handle_call_tool("get_snapshot", {})
        snap_duration = time.time() - start_time
        
        print(f"Snapshot took: {snap_duration:.2f} seconds")
        
        print("\n--- DISTILLED AOM SNAPSHOT (First 30 lines) ---")
        lines = res_snap[0].text.split("\n")
        for line in lines[:30]:
            print(line)
        if len(lines) > 30:
            print(f"... [truncated {len(lines) - 30} lines] ...")
        print("------------------------------------------------")
        
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
    finally:
        # Stop local browser session cleanly
        if phantom_cloud.state.browser:
            try:
                phantom_cloud.state.browser.stop()
                print("\nLocal browser stopped successfully.")
            except Exception as e:
                print(f"Failed to close browser: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_test())
