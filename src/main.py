#!/usr/bin/env python3
"""Entry point of the program.
This main function runs on every node.
Load configuration, Ensure DB is ready, Fetch sites from DB and Start monitoring sites.    
"""

import signal
import asyncio
from utils import logger, load_config_from_file, handl_signals
from keeper import Keeper
from worker import Worker

async def main():
    """This function runs on every node.
    """
    logger.info("Starting")

    signal.signal(signal.SIGINT, handl_signals)

    load_config_from_file()

    # Re-use the Keeper class to fetch sites from DB
    keeper = Keeper(None)
    keeper.check_readiness()
    endpoints_to_be_monitored = keeper.fetch_endpoints()
    logger.info("There are %d endpoints to monitor", len(endpoints_to_be_monitored))

    worker = Worker()
    await worker.run(endpoints_to_be_monitored)

if __name__ == "__main__":
    asyncio.run(main())
    