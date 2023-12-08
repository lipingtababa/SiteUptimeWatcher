from Site import Site
from Stat import Stat
import aiohttp
import asyncio
import time 

class Agent:
    # TODO: Support Post and other HTTP methods
    def __init__(self, statsBuffer: asyncio.Queue):
        self.statsBuffer = statsBuffer

    async def run(self, site: Site):
        async with aiohttp.ClientSession() as session:
            while True:
                stat = Stat(site.url,
                            time.time(),
                            0,
                            0,
                            site.regex,
                            False)
                print(f"Running agent {site.url}")
                try:
                    resp = await session.get(site.url)
                except aiohttp.ClientConnectorError:
                    print(f"Agent {site.url} got error")
                    stat.duration = time.time() - stat.startTime
                    stat.statusCode = 0
                    stat.regexMatch = False
                    stat.regex = None
                    await self.statsBuffer.put(stat)
                    await asyncio.sleep(site.interval)
                    continue
                print(f"Agent {site.url} got response")

                stat.duration = time.time() - stat.startTime
                stat.statusCode = resp.status
                if stat.statusCode == 200:
                    text = await resp.text()
                    if not site.regex:
                        stat.regexMatch = True
                    elif site.regex.match(text):
                        stat.regexMatch = True
                    else:
                        stat.regexMatch = False
                else:
                    # If status code is not 200, then regex matching is not applicable
                    stat.regexMatch = False
                    stat.regex = None
                
                print(f"Agent {site.url} append")
                await self.statsBuffer.put(stat)

                print(f"Agent {site.url} finished")
                await asyncio.sleep(site.interval)

    