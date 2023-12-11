#!/usr/bin/env python3
"""Entry point of the program.
This main function runs on every node.
Load configuration, Ensure DB is ready, Fetch sites from DB and Start monitoring sites.    
"""

import asyncio
from utils import logger, loadConfigFromFile
from keeper import Keeper
from worker import Worker

async def main():
    """This function runs on every node.
    """
    logger.info("Starting")
    loadConfigFromFile()

    # Re-use the Keeper class to fetch sites from DB
    keeper = Keeper(None)
    keeper.checkReadiness()
    endpointsToBeMonitored = keeper.fetchEndpoints()
    logger.info("There are %d URLs to monitor", len(endpointsToBeMonitored))

    worker = Worker()
    await worker.run(endpointsToBeMonitored)

if __name__ == "__main__":
    asyncio.run(main())
    