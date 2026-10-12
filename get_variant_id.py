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
                const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText);
                let foundIds = [];
                for (const s of scripts) {
                    const matches = s.match(/"id":\s*"?(\d{13,15})"?/g) || [];
                    foundIds.push(...matches);
                    const vmatches = s.match(/"ProductVariant",\s*"id":\s*"?(\d+)"?/g) || [];
                    foundIds.push(...vmatches);
                }
                const inputs = Array.from(document.querySelectorAll('input[type="hidden"]')).map(i => ({
                    name: i.name,
                    value: i.value
                }));
                // Check if any links or buttons have variant id
                const allHtml = document.documentElement.outerHTML;
                const vMatches = allHtml.match(/gid:\/\/shopify\/ProductVariant\/(\d+)/g) || [];
                const pMatches = allHtml.match(/gid:\/\/shopify\/Product\/(\d+)/g) || [];
                
                return JSON.stringify({
                    foundIds: foundIds.slice(0, 30),
                    inputs: inputs.filter(i => i.value && /\d{10,}/.test(i.value)),
                    vMatches: vMatches,
                    pMatches: pMatches
                });
            })()"""
            res = await session.call_tool("evaluate", {"expression": expr})
            print(res.content[0].text if res.content else "{}")

asyncio.run(run())
