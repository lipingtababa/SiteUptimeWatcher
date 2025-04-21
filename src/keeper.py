"""This module is a compatibility layer for the original Keeper class.
It uses the new MetricsHandler and EndpointManager classes.
"""
import asyncio
from asyncio import Queue

from metrics_handler import MetricsHandler
from endpoint_manager import EndpointManager

class Keeper:
    """
    This class is a compatibility layer for the original Keeper class.
    It uses the new MetricsHandler and EndpointManager classes.
    """
    def __init__(self, metrics_buffer: Queue):
        self.metrics_buffer = metrics_buffer
        self.metrics_handler = MetricsHandler(metrics_buffer)
        self.endpoint_manager = EndpointManager()

    async def run(self):
        """Run the metrics handler."""
        await self.metrics_handler.run()

    def fetch_endpoints(self, partition_count: int, partition_id: int):
        """Fetch endpoints from the database."""
        return self.endpoint_manager.fetch_endpoints(partition_count, partition_id)

    def check_readiness(self):
        """Ensure DB tables are ready."""
        self.endpoint_manager.check_readiness()
        return self
