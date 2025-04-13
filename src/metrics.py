"""
Module for performance metrics.
"""
import json
import time
import os
from aiohttp import ClientResponse
from endpoint import Endpoint

# Import Datakit client
try:
    from datakit_client import DatakitClient
    DATAKIT_ENABLED = True
    datakit_host = os.getenv("DATAKIT_HOST", "localhost")
    datakit_port = int(os.getenv("DATAKIT_PORT", "9529"))
    datakit_client = DatakitClient(host=datakit_host, port=datakit_port)
except ImportError:
    DATAKIT_ENABLED = False
    print("Datakit client not available. Metrics will not be sent to Datakit.")

class Stat():
    """To store performance metrics for a single request."""
    def __init__(self, endpoint: Endpoint, start_time: float):
        self.endpoint = endpoint
        self.start_time = start_time
        self.duration = 0
        self.status_code = 0
        self.regex_match = False

    def build_from_failed_http_req(self):
        """Update itself for a failed request."""
        assert self.endpoint, "endpoint must be set"
        assert self.start_time, "startTime must be set"

        self.duration = time.time() - self.start_time
        self.status_code = 0
        self.regex_match = False
        
        # Send metrics to Datakit if enabled
        if DATAKIT_ENABLED:
            self._send_metrics_to_datakit()

    async def build_from_successful_http_req(self, response:ClientResponse):
        """Parse HTTP response and update itself."""
        assert self.endpoint, "endpoint must be set before calling initFromHTTPResponse"
        assert self.start_time, "startTime must be set before calling initFromHTTPResponse"

        self.duration = time.time() - self.start_time
        self.status_code = response.status
        if self.status_code == 200:
            text = await response.text()
            if self.endpoint.regex and self.endpoint.regex.match(text):
                self.regex_match = True
                
        # Send metrics to Datakit if enabled
        if DATAKIT_ENABLED:
            self._send_metrics_to_datakit()

    def _send_metrics_to_datakit(self):
        """Send metrics to Datakit."""
        try:
            # Create tags for the metrics
            tags = {
                "endpoint": self.endpoint.url,
                "status_code": str(self.status_code),
                "regex_match": str(self.regex_match).lower()
            }
            
            # Send metrics
            datakit_client.gauge("site_uptime_watcher.response_time", self.duration, tags=tags)
            datakit_client.gauge("site_uptime_watcher.status_code", self.status_code, tags=tags)
            datakit_client.gauge("site_uptime_watcher.regex_match", 1 if self.regex_match else 0, tags=tags)
            
            # Send log
            log_data = {
                "message": f"Endpoint {self.endpoint.url} responded with status {self.status_code} in {self.duration:.2f}s",
                "status": "success" if self.status_code == 200 else "error",
                "duration": self.duration,
                "regex_match": self.regex_match
            }
            datakit_client.log("site_uptime_watcher.log", json.dumps(log_data), tags=tags)
        except Exception as e:
            print(f"Error sending metrics to Datakit: {e}")

    def __str__(self):
        """Output as a json string"""
        return json.dumps(self.__dict__)
