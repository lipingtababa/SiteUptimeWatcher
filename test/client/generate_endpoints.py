#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import random

import psycopg2
import psycopg2.extras

# To import the Site and Keeper class, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent.parent / "src"
sys.path.append(str(src_directory))
from utils import loadConfigFromFile, ENDPOINTS_TABLE_NAME
from keeper import Keeper

class SiteFiller(Keeper):
    def __init__(self):
        # No need to initialize the statsBuffer
        super().__init__(None)

    def FillSites(self):
        self.checkReadiness()

        insert_data = [(f"http://testserver:8000/{i}", "detector", int(random.random())) for i in range(1000)]
        psycopg2.extras.execute_values(
            self.cursor,
            f"TRUNCATE table {ENDPOINTS_TABLE_NAME};INSERT INTO {ENDPOINTS_TABLE_NAME} (url, regex, interval) VALUES %s;",
            insert_data,
            template=None,
            page_size=1000
        )
        self.conn.commit()

def main():
    print("Starting")
    loadConfigFromFile()

    keeper = SiteFiller()
    keeper.FillSites()

if __name__ == "__main__":
    main()