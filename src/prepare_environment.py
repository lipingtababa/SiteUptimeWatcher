#!/usr/bin/env python3

"""
Prepare environment for the program.
"""
from utils import logger, load_config
from endpoint_manager import EndpointManager

def prepare_environment():
    """Check if DB is ready and create tables if necessary."""
    logger.info("Preparing environment")
    load_config()

    endpoint_manager = EndpointManager()
    endpoint_manager.check_readiness()
    logger.info("Environment is ready")

if __name__ == "__main__":
    prepare_environment()
