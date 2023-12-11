""" 
    Worker sends HTTP requests and collect metrics for a URL.
    Worker also provisions keepers.
"""

import time
import asyncio
import aiohttp

from utils import logger, WORKER_KEEPER_RATIO
from endpoint import Endpoint
from keeper import Keeper
from metrics import Stat

class Worker:
    """
    This class sends HTTP requests and collect metrics for a URL.
    """
    def __init__(self):
        # This buffer is used between workers and keepers
        self.statsBuffer = asyncio.Queue()

    async def run(self, endpoints: [Endpoint]):
        """Provision tasks."""
        tasks = []
        # For each endpoint, generate a task which sends HTTP requests to it
        for endpoint in endpoints:
            task = asyncio.create_task(self.monitor(endpoint))
            tasks.append(task)

        # keepers consume buffer and store stats into DB
        for i in range(int(len(endpoints)/WORKER_KEEPER_RATIO)):
            keeper = Keeper(self.statsBuffer)
            keeperTask = asyncio.create_task(keeper.run())
            tasks.append(keeperTask)

        logger.info(f"worker provisioned {len(endpoints)} fetchers and {i+1} keepers.")
        await asyncio.gather(*tasks)

    async def monitor(self, endpoint: Endpoint):
        """ Send HTTP requests and collect metrics from responses."""
        async with aiohttp.ClientSession() as session:
            while True:
                stat = Stat(endpoint, time.time())
                try:
                    resp = await session.get(endpoint.url)
                    await stat.initFromHTTPResponse(resp)
                except Exception as e:
                    logger.error(f"Exception {e} raised when requesting {endpoint.url}")
                    stat.initFromFailedRequest()
                finally:
                    await self.statsBuffer.put(stat)
                    await asyncio.sleep(endpoint.interval)
