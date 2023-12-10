from WorkUnit import WorkUnit
from Keeper import Keeper
from dotenv import load_dotenv
import asyncio
from asyncio import Queue
from Utils import logger

async def main():
    logger.info("Starting")
    load_dotenv()

    # Re-use the Keeper class to fetch sites from DB
    sitesToBeMonitored = Keeper(Queue()).checkReadiness().fetchSites()
    logger.info(f"There are {len(sitesToBeMonitored)} sites to monitor")

    # This is the main entry point of the program
    workUnit = WorkUnit()
    await workUnit.run(sitesToBeMonitored)

if __name__ == "__main__":
    asyncio.run(main())
    