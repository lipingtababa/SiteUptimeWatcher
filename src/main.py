#!/usr/bin/env python3
"""Entry point of the program.
This main function runs on a single core.
Load configuration, Ensure DB is ready, Fetch sites from DB and Start monitoring sites.    
"""
import os
import signal
import asyncio
from utils import logger, load_config, handle_signals, EnvException
from keeper import Keeper
from worker import Worker

async def main():
    """ 
    This is a single thread program.
    Chance is that this process is one of many instances of this program.
    Instances might run on the same machine or different machines.
    """

    partition_count, partition_id = read_partition_count_and_id()
    logger.info("Starting with Partition ID: %d and Partition Count: %d",
                partition_id,
                partition_count)
    signal.signal(signal.SIGINT, handle_signals)

    load_config()
    # Read endpoints which are assigned to this process from DB
    keeper = Keeper(None)
    endpoints = keeper.fetch_endpoints(partition_count, partition_id)
    logger.info("Process [%d] monitors %d endpoints", os.getpid(), len(endpoints))

    worker = Worker()
    await worker.run(endpoints)

def read_partition_count_and_id():
    """Read partition info from env."""

    # Default value is 0 and 1, which means that this process is the only one.
    partition_id = int(os.getenv("PARTITION_ID", "0"))
    partition_count = int(os.getenv("PARTITION_COUNT", "1"))

    # Validate partition_count and partition_id
    if partition_count < 1 or partition_id < 0 or partition_id >= partition_count:
        erro_msg = f"""PARTITION_COUNT [{partition_count}] and PARTITION_ID [{partition_id}] are invalid"""
        logger.error(erro_msg)
        raise EnvException(erro_msg)

    return partition_count, partition_id

if __name__ == "__main__":
    asyncio.run(main())
    