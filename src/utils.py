
"""This module contains some functions that
1. initialize logger
2. load configuration from .env
3. define some constants
"""

import logging
import os
from dotenv import load_dotenv
from detector_exception import EnvException

# define a constant
WORKER_KEEPER_RATIO = 5000
KEEPER_SLEEP_INTERVAL = 0.2


RUNNING_STATUS = True

# install a signal handler
# pylint: disable=unused-argument, global-statement
def handle_signals(signal, frame):
    """Update the global variable so work loop would exit gracefully."""
    global RUNNING_STATUS
    RUNNING_STATUS = False

def init_logger():
    """Initialize global variable logger."""
    thelogger = logging.getLogger('detector_logger')
    thelogger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(process)d - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
        )
    handler.setFormatter(formatter)
    thelogger.addHandler(handler)
    return thelogger

logger = init_logger()

def load_config_from_file(file =".env"):
    """Load configuration from .env or a specified file."""
    load_dotenv(file)

    required_env_vars = ["DB_HOST",
                         "DB_PORT",
                         "DB_USER",
                         "DB_PASSWORD",
                         "DB_NAME"]
    if any(os.getenv(var) is None for var in required_env_vars):
        raise EnvException("DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME must be set")

    if os.getenv("DB_PORT").isdigit() is False:
        raise EnvException("DB_PORT must be an integer")
