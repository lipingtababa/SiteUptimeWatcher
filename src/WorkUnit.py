from Worker import Worker
from Site import Site
from Keeper import Keeper
import asyncio
from Utils import logger

class WorkUnit:
    def __init__(self):
        # This buffer is used between workers and keepers
        self.statsBuffer = asyncio.Queue()

    async def run(self, sites: [Site]):
        tasks = []
        # workers detect sites and put stats into buffer
        for site in sites:
            worker = Worker(self.statsBuffer)
            task = asyncio.create_task(worker.run(site))
            tasks.append(task)

        # keepers consume buffer and store stats into DB
        for i in range(int(len(sites)/500)):
            keeper = Keeper(self.statsBuffer)
            keeperTask = asyncio.create_task(keeper.run())
            tasks.append(keeperTask)

        logger.info(f"WorkUnit provisioned {len(sites)} workers and {i+1} keepers.")
        await asyncio.gather(*tasks)
