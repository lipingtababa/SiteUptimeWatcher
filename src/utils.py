"""This module contains some functions that
1. initialize logger
2. load configuration from .env
3. define some constants
"""

import logging
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# define a constant
WORKER_KEEPER_RATIO = 5000
KEEPER_SLEEP_INTERVAL = 0.2

RUNNING_STATUS = True

class EnvException(Exception):
    """Raised if required environment variables are not set or invalid."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

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
                         "DB_NAME"]
    if any(os.getenv(var) is None for var in required_env_vars):
        raise EnvException("DB_HOST, DB_PORT, DB_USER, DB_NAME must be set in the file")

    if os.getenv("DB_PORT").isdigit() is False:
        raise EnvException("DB_PORT must be an integer")

def get_ssm_parameter(param_name, with_decryption=True):
    """Get a parameter from AWS SSM Parameter Store."""
    session = boto3.session.Session()
    client = session.client(
        service_name='ssm',
        region_name='us-east-1'
    )
    try:
        parameter = client.get_parameter(
            Name=param_name,
            WithDecryption=with_decryption
        )
        return parameter['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Error retrieving parameter: {e}")
        return None

def load_secrets_from_secrets_manager():
    """Load secrets from AWS SSM Parameter Store."""
    # Get database connection parameters from SSM
    db_host = get_ssm_parameter('/watcher/db/host')
    db_port = get_ssm_parameter('/watcher/db/port')
    db_name = get_ssm_parameter('/watcher/db/name')
    db_user = get_ssm_parameter('/watcher/db/user')
    db_password = get_ssm_parameter('/watcher/db/password', with_decryption=True)

    if all([db_host, db_port, db_name, db_user, db_password]):
        os.environ["DB_HOST"] = db_host
        os.environ["DB_PORT"] = db_port
        os.environ["DB_NAME"] = db_name
        os.environ["DB_USER"] = db_user
        os.environ["DB_PASSWORD"] = db_password
        return True
    return False

def load_config():
    """Load configuration from .env or a specified file."""
    load_config_from_file()
    if not load_secrets_from_secrets_manager():
        raise EnvException("Failed to retrieve database connection parameters from SSM Parameter Store")
