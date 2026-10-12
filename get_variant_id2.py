import asyncio
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

SSE_URL = "http://127.0.0.1:8000/sse/?token=ph_live_D2aZuYtdGL6tUfuV2egoxp"

async def run():
    async with sse_client(SSE_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            expr = r"""(() => {
                // Search for any numbers that look like variant IDs (14 digits) in the DOM or window
                const text = document.documentElement.outerHTML;
                const matches = text.match(/\b505\d{11}\b|\b50\d{12}\b|\b67\d{12}\b|\b103\d{11}\b/g) || [];
                
                // Let's also check if there is an apollo cache or relay store
                let apolloKeys = [];
                for (const key of Object.keys(window)) {
                    if (key.includes('apollo') || key.includes('relay') || key.includes('DATA') || key.includes('STATE') || key.includes('Shopify')) {
                        apolloKeys.push(key);
                    }
                }
                
                return JSON.stringify({
                    idMatches: Array.from(new Set(matches)),
                    interestingWindowKeys: apolloKeys
                });
            })()"""
            res = await session.call_tool("evaluate", {"expression": expr})
            print(res.content[0].text if res.content else "{}")

asyncio.run(run())
