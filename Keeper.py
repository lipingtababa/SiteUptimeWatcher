from Stat import Stat
import psycopg2
import psycopg2.extras

import os
from Exceptions import EnvException
from datetime import datetime, timezone
from Site import Site 
from asyncio import Queue
import asyncio

class Keeper:
    def __init__(self, statsBuffer: Queue):
        self.connect2DB()
        self.statsBuffer = statsBuffer

    async def run(self):
        print("Keeper running")
        while True:
            queueSize = self.statsBuffer.qsize()
            print(f"Stats size {queueSize}")
            stats = []
            consumerLength = queueSize if queueSize < 100 else 100
            print(f"Keeper consumes {consumerLength}")
            for i in range(consumerLength):
                stat = await self.statsBuffer.get()
                stats.append(stat)
                self.statsBuffer.task_done()
            self.insert(stats)
            await asyncio.sleep(0.1)

    def connect2DB(self):
        self.conn = psycopg2.connect(
            dbname = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor()

    def checkReadiness(self):
        self.connect2DB()
        # check if sites table is present 
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sites');")
        is_sites_table = self.cursor.fetchone()[0]
        if not is_sites_table:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sites (
                    url VARCHAR(255) PRIMARY KEY,
                    regex VARCHAR(255),
                    interval INT
                );
            """)
            self.conn.commit()

        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        self.conn.commit()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                time TIMESTAMP NOT NULL,
                url VARCHAR(255),
                duration INT,
                statusCode INT,
                regex VARCHAR(255),
                regexMatch BOOLEAN
            );
        """)
        self.conn.commit()

        self.cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM timescaledb_information.hypertables
            WHERE hypertable_name = 'stats'
        );
        """)
        is_hypertable = self.cursor.fetchone()[0]
        if not is_hypertable:
            self.cursor.execute("SELECT create_hypertable('stats', 'time');")
            self.conn.commit()
        
        return self

    def insert(self, stats: [Stat]):
        if len(stats) == 0:
            return
        # use extras to insert multiple rows
        psycopg2.extras.execute_values(
            self.cursor,
            """
            INSERT INTO stats (time, url, duration, statusCode, regex, regexMatch)
            VALUES %s;
            """,
            [(datetime.fromtimestamp(stat.startTime, timezone.utc),
              stat.url, 
              stat.duration, 
              stat.statusCode, 
              stat.regex.pattern if stat.regex else "", 
              stat.regexMatch) for stat in stats],
            template=None,
            page_size=1000
        )
        self.conn.commit()


    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def fetchSites(self):
        self.cursor.execute("SELECT url, regex, interval FROM sites;")
        rows = self.cursor.fetchall()
        sites = []
        for row in rows:
            sites.append(Site(row[0], row[1], row[2]))
        return sites
