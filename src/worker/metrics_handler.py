"""This module handles metrics collection and sending to TrueWatch.
1. Collect metrics from buffer
2. Send metrics to TrueWatch
"""
import os
import asyncio
from typing import List
from asyncio import Queue
import requests

from src.utils import logger
from src.worker.metrics import Stat

PG_BATCH_SIZE = 1000

# TrueWatch configuration
TRUEWATCH_ENABLED = os.getenv("TRUEWATCH_ENABLED", "true") == "true"
truewatch_host = os.getenv("TRUEWATCH_HOST", "localhost")
truewatch_port = int(os.getenv("TRUEWATCH_PORT", "9529"))
truewatch_url = f"http://{truewatch_host}:{truewatch_port}"

class MetricsHandler:
    """Handler for processing and storing metrics."""
    
    def __init__(self, metrics_buffer: Queue):
        """Initialize the metrics handler."""
        self.metrics_buffer = metrics_buffer
        self._running = True

    def stop(self):
        """Stop the metrics handler."""
        self._running = False

    async def run(self):
        """Run the metrics handler."""
        logger.info(f"MetricsHandler {id(self)} started")
        while self._running:
            try:
                queue_size = self.metrics_buffer.qsize()
                if queue_size > 0:
                    logger.info(f"Processing {queue_size} metrics")
                    metrics = []
                    consumer_length = queue_size if queue_size < PG_BATCH_SIZE else PG_BATCH_SIZE
                    logger.info(f"MetricsHandler consumes {consumer_length}")
                    for _ in range(consumer_length):
                        metric = await self.metrics_buffer.get()
                        metrics.append(metric)
                        await self._process_metric(metric)
                        self.metrics_buffer.task_done()
                    # Send metrics to TrueWatch if enabled
                    self._send_metrics_to_truewatch(metrics)
            except Exception as e:
                logger.error(f"Error processing metric: {e}")
                await asyncio.sleep(1)
        logger.info("Exiting MetricsHandler loop")

    async def _process_metric(self, metric: Stat):
        """Process a single metric."""
        try:
            # TODO: Store metric in database
            logger.info(f"Processed metric for {metric.endpoint.url}")
        except Exception as e:
            logger.error(f"Error storing metric: {e}")

    def _send_metrics_to_truewatch(self, metrics: List[Stat]):
        """Send metrics to TrueWatch using HTTP API.
        TrueWatch expects metrics in the following format:
        {
            "measurement": "site_uptime_watcher",
            "tags": {
                "endpoint": "url",
                "status_code": "code",
                "regex_match": "true/false"
            },
            "fields": {
                "response_time": value,
                "status_code": value,
                "regex_match": 1/0
            }
        }
        """
        try:
            # Prepare metrics data for all metrics in the batch
            metrics_data = []
            for metric in metrics:
                # Create tags for the metrics
                tags = {
                    "endpoint": metric.endpoint.url,
                    "status_code": str(metric.status_code),
                    "regex_match": str(metric.regex_match).lower()
                }
                # Add metrics data
                metrics_data.append({
                    "measurement": "site_uptime_watcher",
                    "tags": tags,
                    "fields": {
                        "response_time": metric.duration,
                        "status_code": metric.status_code,
                        "regex_match": 1 if metric.regex_match else 0
                    }
                })
            # Send metrics via HTTP API
            metrics_url = f"{truewatch_url}/v1/write/metrics"
            response = requests.post(metrics_url, json=metrics_data, timeout=5)
            if response.status_code != 200:
                logger.error(f"Error sending metrics to TrueWatch: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error sending metrics to TrueWatch: {e}")
            