import re

class Site:
    def __init__(self, url, regex, interval=5):
        self.url = url
        self.regex = re.compile(regex)
        self.interval = interval