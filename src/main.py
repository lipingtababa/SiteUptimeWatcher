#!/usr/bin/env python3
"""Entry point of the program.
This main function runs on every node.
Load configuration, Ensure DB is ready, Fetch sites from DB and Start monitoring sites.    
"""

import asyncio
from Utils import logger, loadConfigFromFile
from worker import Worker
from Keeper import Keeper


async def main():
    """This function runs on every node.
    """
    logger.info("Starting")
    loadConfigFromFile()

    # Re-use the Keeper class to fetch sites from DB
    sitesToBeMonitored = Keeper(None).checkReadiness().fetchSites()
    logger.info("There are %d URLs to monitor", len(sitesToBeMonitored))

    worker = Worker()
    await worker.run(sitesToBeMonitored)

if __name__ == "__main__":
    asyncio.run(main())
    