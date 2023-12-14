"""
Module for performance metrics.
"""
import json
import time
from endpoint import Endpoint
from aiohttp import ClientResponse

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

    async def build_from_successful_http_req(self, response:ClientResponse):
        """Parse HTTP response and update itself."""
        assert self.endpoint, "endpoint must be set before calling initFromHTTPResponse"
        assert self.start_time, "startTime must be set before calling initFromHTTPResponse"

        self.duration = time.time() - self.start_time
        self.status_code = response.status
        if self.status_code == 200:
            text = await response.text()
            
            print(text)
            if self.endpoint.regex and self.endpoint.regex.match(text):
                self.regex_match = True

    def __str__(self):
        """Output as a json string"""
        return json.dumps(self.__dict__)
