import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import psycopg2
import psycopg2.extras
from asyncio import Queue
import random

# To import the Site and Keeper class, we need to add the parent directory to the path
src_directory = Path(__file__).resolve().parent.parent.parent / "src"
print(f"Adding {src_directory} to path")
sys.path.append(str(src_directory))

from Keeper import Keeper 

class SiteFiller(Keeper):
    def __init__(self, statsBuffer: Queue):
        super().__init__(statsBuffer)

    def FillSites(self):
        self.checkReadiness()

        insert_data = [(f"http://testserver:8000/{i}", "detector", int(random.random())) for i in range(2000)]
        psycopg2.extras.execute_values(
            self.cursor,
            "TRUNCATE table sites;INSERT INTO sites (url, regex, interval) VALUES %s;",
            insert_data,
            template=None,
            page_size=1000
        )
        self.conn.commit()

def main():
    print("Starting")
    load_dotenv()

    keeper = SiteFiller(asyncio.Queue())
    keeper.FillSites()

if __name__ == "__main__":
    main()