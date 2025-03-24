"""
This module contains the Endpoint class"""
import re

# pylint: disable=too-few-public-methods
class Endpoint:
    """
    An Endpoint is a URL with 
        1. a regex to match against the response body.
        2. an interval to send requests.
    """
    def __init__(self, endpoint_id, url, regex, interval):
        """Never trust the DB, always validate your input"""
        assert endpoint_id, "id is required"
        assert url, "url is required"
        assert interval, "interval is required"
        assert 5 <= interval <= 300, "interval must be greater than 5 and less than 300"

        self.endpoint_id = endpoint_id
        self.url = url
        if regex:
            self.regex = re.compile(regex)
        self.interval = interval
