"""
Module for performance metrics.
"""
import json
import time
from dataclasses import dataclass
from typing import Optional

from src.endpoint import Endpoint

@dataclass
class Stat:
    """Class for storing endpoint monitoring statistics."""
    endpoint: Endpoint
    timestamp: float
    status_code: Optional[int] = None
    duration: Optional[float] = None
    regex_match: Optional[bool] = None
    
    async def build_from_successful_http_req(self, response):
        """Build stats from a successful HTTP response."""
        self.status_code = response.status
        self.duration = time.time() - self.timestamp
            
        if self.status_code == 200 and self.endpoint.regex:
            text = await response.text()
            self.regex_match = bool(self.endpoint.regex.match(text))
        else:
            self.regex_match = False
    
    def build_from_failed_http_req(self):
        """Build stats from a failed HTTP request."""
        self.status_code = 0
        self.regex_match = False
        self.duration = time.time() - self.timestamp

    def __str__(self):
        """Output as a json string"""
        return json.dumps(self.__dict__)
