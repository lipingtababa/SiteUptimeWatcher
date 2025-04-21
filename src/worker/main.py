#!/usr/bin/env python3
"""Entry point of the program.
This main function runs on a single core.
Load configuration, Ensure DB is ready, Fetch sites from DB and Start monitoring sites.    
"""
import signal
import asyncio
import os

from src.utils import logger, load_config
from src.worker.worker import Worker
from src.worker.metrics_handler import MetricsHandler
from src.endpoint_manager import EndpointManager

class WorkerManager:
    """Manager class to handle worker lifecycle."""
    
    def __init__(self):
        """Initialize the worker manager."""
        self.worker = None
        
    def set_worker(self, worker):
        """Set the worker instance."""
        self.worker = worker
        
    def stop_worker(self):
        """Stop the worker."""
        if self.worker:
            self.worker.stop()

# Create a global worker manager instance
worker_manager = WorkerManager()

# pylint: disable=unused-argument
def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM signals."""
    logger.info("Received signal to terminate")
    worker_manager.stop_worker()

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
        worker_manager.set_worker(worker)
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
    """Main entry point for the worker."""
    # Load configuration
    load_config()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create worker and metrics handler
    metrics_buffer = asyncio.Queue()
    
    # Initialize endpoint manager
    endpoint_manager = EndpointManager()
    endpoint_manager.check_readiness()
    
    # Fetch endpoints for this partition
    endpoints = endpoint_manager.fetch_endpoints(os.getenv("PARTITION_COUNT"), os.getenv("PARTITION_ID"))
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
    worker_manager.set_worker(worker)
    tasks.append(asyncio.create_task(worker.run(endpoints)))
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
    