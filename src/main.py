from WorkUnit import WorkUnit
from Keeper import Keeper
import asyncio
from asyncio import Queue
from Utils import logger, loadConfigFromFile

async def main():
    logger.info("Starting")
    loadConfigFromFile()

    # Re-use the Keeper class to fetch sites from DB
    sitesToBeMonitored = Keeper(None).checkReadiness().fetchSites()
    logger.info(f"There are {len(sitesToBeMonitored)} sites to monitor")

    # This is the main entry point of the program
    workUnit = WorkUnit()
    await workUnit.run(sitesToBeMonitored)

if __name__ == "__main__":
    asyncio.run(main())
    