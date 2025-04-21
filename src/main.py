#!/usr/bin/env python3
"""Entry point of the program.
This main function runs on a single core.
Load configuration, Ensure DB is ready, Fetch sites from DB and Start monitoring sites.    
"""
import os
import signal
import asyncio
import sys
from multiprocessing import Process, cpu_count
from utils import logger, load_config, handle_signals, EnvException, RUNNING_STATUS
from worker import Worker
from metrics_handler import MetricsHandler
from endpoint_manager import EndpointManager

def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM signals."""
    logger.info("Received signal to terminate")
    global RUNNING_STATUS
    RUNNING_STATUS = False
    sys.exit(0)

async def run_worker(partition_id: int, partition_count: int, metrics_buffer):
    """Run a worker process."""
    try:
        # Initialize endpoint manager
        endpoint_manager = EndpointManager()
        endpoint_manager.check_readiness()
        
        # Fetch endpoints for this partition
        endpoints = endpoint_manager.fetch_endpoints(partition_count, partition_id)
        
        # Create and run worker
        worker = Worker(metrics_buffer)
        await worker.run(endpoints)
    except Exception as e:
        logger.error(f"Error in worker {partition_id}: {e}")
        raise e

async def run_metrics_handler(metrics_buffer):
    """Run the metrics handler."""
    try:
        metrics_handler = MetricsHandler(metrics_buffer)
        await metrics_handler.run()
    except Exception as e:
        logger.error(f"Error in metrics handler: {e}")
        raise e

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
    metrics_buffer = asyncio.Queue()
    
    # Initialize endpoint manager
    endpoint_manager = EndpointManager()
    endpoint_manager.check_readiness()
    
    # Fetch endpoints for this partition
    endpoints = endpoint_manager.fetch_endpoints(partition_count, partition_id)
    if not endpoints:
        logger.warning("No endpoints found in database")
        return
    
    # Create tasks for metrics handler and worker
    tasks = []
    
    # Add metrics handler task
    metrics_handler = MetricsHandler(metrics_buffer)
    tasks.append(asyncio.create_task(metrics_handler.run()))
    
    # Add worker task
    worker = Worker(metrics_buffer)
    tasks.append(asyncio.create_task(worker.run(endpoints)))
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

def read_partition_count_and_id():
    """Read partition count and ID from environment variables."""
    partition_count = int(os.getenv("PARTITION_COUNT", "1"))
    partition_id = int(os.getenv("PARTITION_ID", "0"))
    return partition_count, partition_id

if __name__ == "__main__":
    asyncio.run(main())
    