"""
This module contains the Endpoint class"""
import re

class Endpoint:
    """
    An Endpoint is a URL with 
        1. a regex to match against the response body.
        2. an interval to send requests.
    """
    def __init__(self, endpoint_id, url, regex, interval=5):
        """Never trust the DB, always validate your input"""
        assert endpoint_id, "id is required"
        assert url, "url is required"
        assert interval % 5 == 0 and interval <=300 and interval >=5, "interval must be greater than 0"

        self.endpoint_id = endpoint_id
        self.url = url
        if regex:
            self.regex = re.compile(regex)
        self.interval = interval