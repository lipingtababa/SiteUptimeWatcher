"""
Module for performance metrics.
"""
import json
import time
from endpoint import Endpoint

class Stat():
    """To store performance metrics for a single request."""
    def __init__(self, endpoint: Endpoint, startTime: float):
        self.endpoint = endpoint
        self.startTime = startTime
        self.duration = 0
        self.statusCode = 0
        self.regexMatch = False

    def initFromFailedRequest(self):
        """Update itself for a failed request."""
        assert self.endpoint, "endpoint must be set"
        assert self.startTime, "startTime must be set"

        self.duration = time.time() - self.startTime
        self.statusCode = 0
        self.regexMatch = False

    async def initFromHTTPResponse(self, response):
        """Parse HTTP response and update itself."""
        assert self.endpoint, "endpoint must be set before calling initFromHTTPResponse"
        assert self.startTime, "startTime must be set before calling initFromHTTPResponse"

        self.duration = time.time() - self.startTime
        self.statusCode = response.status
        if self.statusCode == 200:
            text = await response.text()
            if self.endpoint.regex and self.endpoint.regex.match(text):
                self.regexMatch = True

    def __str__(self):
        """Output as a json string"""
        return json.dumps(self.__dict__)
