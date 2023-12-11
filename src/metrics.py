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
        assert self.endpoint, "endpoint must be set"
        assert self.startTime, "startTime must be set"

        self.duration = time.time() - self.startTime
        self.statusCode = response.status
        if self.statusCode == 200:
            # There is a chance that the body of the HTTP response
            # has not been fully downloaded
            text = await response.text()
            if not self.endpoint.regex or self.endpoint.regex.match(text):
                self.regexMatch = True
            else:
                self.regexMatch = False
        else:
            # If status code is not 200,
            # then regex matching is not applicable
            self.regexMatch = False

    def __str__(self):
        """Output as a json string"""
        return json.dumps(self.__dict__)

