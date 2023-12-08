from Agent import Agent
from Site import Site
from Keeper import Keeper
import asyncio

class WorkUnit:
    def __init__(self):
        # All async agents in the same thread will write to the same buffer
        self.statsBuffer = asyncio.Queue()

    async def run(self, sites: [Site]):
        tasks = []
        for site in sites:
            agent = Agent(self.statsBuffer)
            task = asyncio.create_task(agent.run(site))
            tasks.append(task)

        # keeper consumes buffer and store stats into DB
        for i in range(int(len(sites)/500)):
            keeper = Keeper(self.statsBuffer)
            keeperTask = asyncio.create_task(keeper.run())
            tasks.append(keeperTask)

        await asyncio.gather(*tasks)
