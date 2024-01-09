#!/usr/bin/env python3

"""
Prepare environment for the program.
"""
from utils import logger, load_config
from keeper import Keeper

def prepare_environment():
    """Check if DB is ready and create tables if necessary."""
    logger.info("Preparing environment")
    load_config()

    keeper = Keeper(None)
    keeper.check_readiness()
    logger.info("Environment is ready")

if __name__ == "__main__":
    prepare_environment()
