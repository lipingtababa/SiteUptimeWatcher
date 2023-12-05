from Agent import Agent
from Site import Site
import asyncio

class WorkUnit:
    async def run(self):
        for i in range(0, 3):
            print("Running work unit")
            await asyncio.sleep(interval)
            agent = Agent(Site(f"https://www.example.com/search?q={i}", ".*"))
            await agent.run()

async def main():
    print("Running main")
    workUnit = WorkUnit()
    await workUnit.run()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    