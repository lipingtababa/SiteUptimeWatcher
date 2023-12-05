from Site import Site
import aiohttp
import asyncio
import time 

class Agent:
    # TODO: Support Post and other HTTP methods
    def __init__(self, site):
        self.site = site

    async def run(self):
        async with aiohttp.ClientSession() as session:
            for i in range(0, 6):
                print(f"Running agent {self.site.url} {i}")
                resp = await session.get(self.site.url)
                print(resp.status)

async def run_in_parrel(sites):

    tasks = []
    for site in sites:
        agent = Agent(site)
        # construct a list of tasks
        task = asyncio.create_task(agent.run())
        tasks.append(task)
    # run the tasks
    await asyncio.gather(*tasks)  # 并发运行所有任务

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    sites = [Site(f"https://www.example.com/search?q={i}", ".*") for i in range(0, 3)]
    loop.run_until_complete(run_in_parrel(sites))
    time.sleep(10)
    loop.close()

    