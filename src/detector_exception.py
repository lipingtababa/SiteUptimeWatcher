"""
This file contains the custom exceptions for the detector.
"""
class EnvException(Exception):
    """
    Raised if required environment variables are not set or invalid.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
