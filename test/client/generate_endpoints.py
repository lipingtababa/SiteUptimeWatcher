#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to fill the DB with random endpoints."""

import sys
from pathlib import Path
import random

import psycopg2
import psycopg2.extras

# To import the Site and Keeper class, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent.parent / "src"
sys.path.append(str(src_directory))
from utils import loadConfigFromFile
from keeper import Keeper, ENDPOINTS_TABLE_NAME

# pylint: disable=too-few-public-methods
class SiteFiller(Keeper):
    """This class is used to fill the DB with random endpoints."""
    def __init__(self):
        # No need to initialize the statsBuffer
        super().__init__(None)

    def FillSites(self):
        """ IMPOTANT! It will erase any existing data in the DB."""
        self.checkReadiness()

        insert_data = [
            (f"http://testserver:8000/{i}",
             "welcome",
             random.randint(5, 30)) for i in range(10)
             ]
        psycopg2.extras.execute_values(
            self.cursor,
            f"""TRUNCATE table {ENDPOINTS_TABLE_NAME} CASCADE;
                INSERT INTO {ENDPOINTS_TABLE_NAME} (url, regex, interval) VALUES %s;
            """,
            insert_data,
            template=None,
            page_size=1000
        )
        self.conn.commit()

def main():
    """ This is a independent script."""
    print("Starting")
    loadConfigFromFile()

    keeper = SiteFiller()
    keeper.FillSites()

if __name__ == "__main__":
    main()
