#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to fill the DB with random endpoints."""

import random
import psycopg2
import psycopg2.extras

from src.utils import load_config, logger
from src.endpoint_manager import EndpointManager, ENDPOINTS_TABLE_NAME

# Define batch size for PostgreSQL operations
PG_BATCH_SIZE = 1000

# pylint: disable=too-few-public-methods
class SiteGenerator:
    """This class is used to fill the DB with random endpoints."""
    def __init__(self):
        self.endpoint_manager = EndpointManager()

    def generate_endpoints(self):
        """ IMPORTANT! It will erase any existing data in the DB."""
        conn = self.endpoint_manager.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"TRUNCATE table {ENDPOINTS_TABLE_NAME} CASCADE;")
                insert_data = [
                    (f"http://testserver:8001/{i}",
                    ".*welcome",
                    random.randint(5, 30)) for i in range(20000)
                    ]
                psycopg2.extras.execute_values(
                    cursor,
                    f"""
                        INSERT INTO {ENDPOINTS_TABLE_NAME} (url, regex, interval) VALUES %s;
                    """,
                    insert_data,
                    template=None,
                    page_size=PG_BATCH_SIZE
                )
                conn.commit()
        except Exception as e:
            logger.error(e)
            conn.rollback()
        finally:
            self.endpoint_manager.release_connection(conn)

def main():
    """ This is an independent script."""
    logger.info("Generating endpoints")
    load_config()

    generator = SiteGenerator()
    generator.generate_endpoints()

if __name__ == "__main__":
    main()
