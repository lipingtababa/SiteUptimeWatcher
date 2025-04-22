#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to fill the DB with random endpoints."""

import random
import psycopg2
import psycopg2.extras

from src.utils import load_config, logger
from src.worker.keeper import Keeper, ENDPOINTS_TABLE_NAME, PG_BATCH_SIZE

# pylint: disable=too-few-public-methods
class SiteGenerator(Keeper):
    """This class is used to fill the DB with random endpoints."""
    def __init__(self):
        # No need to initialize the statsBuffer
        super().__init__(None)

    def generate_endpoints(self):
        """ IMPORTANT! It will erase any existing data in the DB."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"TRUNCATE table {ENDPOINTS_TABLE_NAME} CASCADE;")
                    insert_data = [
                        (f"http://testserver:8000/{i}",
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
            self.release_connection(conn)

def main():
    """ This is an independent script."""
    logger.info("Generating endpoints")
    load_config()

    keeper = SiteGenerator()
    keeper.generate_endpoints()

if __name__ == "__main__":
    main()
