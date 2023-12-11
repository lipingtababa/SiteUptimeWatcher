import logging
import os
from dotenv import load_dotenv
from detector_expections import EnvException

# define a constant
WORKER_KEEPER_RATIO = 500
KEEPER_SLEEP_INTERVAL = 0.1


def initLogger():
    logger = logging.getLogger('detector_logger')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = initLogger()

def loadConfigFromFile(file =".env"):
    load_dotenv(file)
    if os.getenv("DB_HOST") is None or os.getenv("DB_PORT") is None or os.getenv("DB_USER") is None or os.getenv("DB_PASSWORD") is None or os.getenv("DB_NAME") is None:
        raise EnvException("DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME must be set")
    if os.getenv("DB_PORT").isdigit() is False:
        raise EnvException("DB_PORT must be an integer")

