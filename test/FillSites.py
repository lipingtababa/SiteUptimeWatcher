import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import psycopg2
import psycopg2.extras
from asyncio import Queue

# To import the Site and Keeper class, we need to add the parent directory to the path
current_directory = Path(__file__).resolve().parent
parent_directory = current_directory.parent
sys.path.append(str(parent_directory))

from Keeper import Keeper 

class SiteFiller(Keeper):
    def __init__(self, statsBuffer: Queue):
        super().__init__(statsBuffer)

    def FillSites(self):
        self.checkReadiness()

        insert_data = [(f"http://localhost:9876/{i}", "detector", 5) for i in range(5000)]
        psycopg2.extras.execute_values(
            self.cursor,
            "INSERT INTO sites (url, regex, interval) VALUES %s;",
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