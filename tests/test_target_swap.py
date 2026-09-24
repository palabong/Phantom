import asyncio
import time
import nodriver as uc

async def main():
    browser = await uc.start()
    page = await browser.get("https://bot.sannysoft.com/")
    print("Initial target id:", page.target_id)
    await asyncio.sleep(5)
    print("After 5s, target id:", page.target_id)
    try:
        res = await page.send(uc.cdp.runtime.evaluate("document.title"))
        print("Title:", res)
    except Exception as e:
        print("Error evaluating:", e)
        
    try:
        await browser.update_targets()
        page = browser.main_tab
        print("New target id:", page.target_id)
        res = await page.send(uc.cdp.runtime.evaluate("document.title"))
        print("Title with main_tab:", res)
    except Exception as e:
        print("Error with main_tab:", e)
    browser.stop()

if __name__ == "__main__":
    asyncio.run(main())