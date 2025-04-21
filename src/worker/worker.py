""" 
    Worker sends HTTP requests and collect metrics for a URL.
    Worker also provisions keepers.
"""

import asyncio
import time
import re
from typing import List
import aiohttp

from src.utils import logger
from src.endpoint import Endpoint
from src.worker import metrics

class Worker:
    """Worker class to handle endpoint monitoring."""
    
    def __init__(self, stats_buffer=None):
        """Initialize the worker."""
        # This buffer is used between workers and keepers
        self.statsBuffer = stats_buffer if stats_buffer is not None else asyncio.Queue()
        self.session = None
        self._running = True

    async def __aenter__(self):
        """Set up aiohttp session."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up aiohttp session."""
        if self.session:
            await self.session.close()

    def stop(self):
        """Stop the worker."""
        self._running = False

    async def run(self, endpoints: List[Endpoint]):
        """Run the worker with the given endpoints."""
        logger.info(f"Worker {id(self)} started")
        tasks = []
        for endpoint in endpoints:
            tasks.append(asyncio.create_task(self.monitor(endpoint)))
        await asyncio.gather(*tasks)
        logger.info("Exiting the worker loop")

    async def monitor(self, endpoint: Endpoint):
        """ Send HTTP requests and collect metrics from responses."""
        async with aiohttp.ClientSession() as session:
            while self._running:
                # Create a new metric object
                metric = metrics.Stat(endpoint, time.time())
                try:
                    resp = await session.get(endpoint.url)
                    await metric.build_from_successful_http_req(resp)
                except Exception as e:
                    logger.error(f"Error monitoring {endpoint.url}: {e}")
                    metric.build_from_failed_http_req(e)
                finally:
                    await self.statsBuffer.put(metric)
                    await asyncio.sleep(endpoint.interval)
            logger.info("Exiting the monitor loop")

    def process_endpoint(self, endpoint: Endpoint):
        """Process a single endpoint."""
        asyncio.run(self._process_endpoint(endpoint))

    async def _process_endpoint(self, endpoint: Endpoint):
        """Process a single endpoint asynchronously."""
        if not self.session:
            async with self:
                await self._check_endpoint(endpoint)
        else:
            await self._check_endpoint(endpoint)

    async def _check_endpoint(self, endpoint: Endpoint):
        """Check if an endpoint is up and matches the regex pattern."""
        try:
            async with self.session.get(endpoint.url, timeout=30) as response:
                content = await response.text()
                is_up = response.status == 200
                
                if is_up and endpoint.regex:
                    is_up = bool(re.search(endpoint.regex, content))
                
                logger.info(f"Endpoint {endpoint.url} is {'up' if is_up else 'down'}")
                # TODO: Store metrics in database
                
        except Exception as e:
            logger.error(f"Error checking endpoint {endpoint.url}: {e}")
            # TODO: Store error metrics in database
            