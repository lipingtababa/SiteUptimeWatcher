from WorkUnit import WorkUnit
from Keeper import Keeper
from Site import Site 
from dotenv import load_dotenv
import asyncio
from asyncio import Queue
import os

async def main():
    print("Starting")
    load_dotenv()

    sites = Keeper(Queue()).checkReadiness().fetchSites()
    print(f"Found {len(sites)} sites")

    workUnit = WorkUnit()

    await workUnit.run(sites)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    