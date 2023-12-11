"""This module deals with the database.
1. Ensure DB is ready
2. Fetch sites from DB
3. Insert stats into DB
"""
import os
from datetime import datetime, timezone
import re

from asyncio import Queue
import asyncio
import psycopg2
import psycopg2.extras

from utils import logger, KEEPER_SLEEP_INTERVAL
from metrics import Stat
from endpoint import Endpoint

ENDPOINTS_TABLE_NAME = 'endpoints'
METRICS_TABLE_NAME = 'metrics'

class Keeper:
    """
    This class deals with the database.
    """
    def __init__(self, statsBuffer: Queue):
        self.connect2DB()
        self.statsBuffer = statsBuffer

    async def run(self):
        """ Consume stats from statsBuffer and insert them into DB."""
        logger.info("A keeper started")
        while True:
            queueSize = self.statsBuffer.qsize()
            stats = []
            consumerLength = queueSize if queueSize < 1000 else 1000
            logger.info(f"Keeper consumes {consumerLength}")
            for _ in range(consumerLength):
                # TODO There must be a better way
                # to consume multiple items from a queue
                stat = await self.statsBuffer.get()
                stats.append(stat)
                self.statsBuffer.task_done()
            self.insert(stats)
            await asyncio.sleep(KEEPER_SLEEP_INTERVAL)

    def connect2DB(self):
        """Connect to DB."""
        self.conn = psycopg2.connect(
            dbname = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor()
        return self

    def assureEndpointTable(self):
        """Check if endpoint table is present"""
        self.cursor.execute(
            f"""SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = '{ENDPOINTS_TABLE_NAME}');
            """
            )
        present = self.cursor.fetchone()[0]
        if not present:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {ENDPOINTS_TABLE_NAME} (
                    endpoint_id SERIAL PRIMARY KEY,
                    url VARCHAR(255) not null,
                    regex VARCHAR(255),
                    interval INT not null
                );
            """)
            self.conn.commit()
        return self

    def fetchEndpoints(self):
        """Fetch URLs to be monitored from table sites."""
        self.cursor.execute(
            f"SELECT endpoint_id, url, regex, interval FROM {ENDPOINTS_TABLE_NAME};"
            )
        rows = self.cursor.fetchall()
        endpoints = []
        for row in rows:
            try:
                endpoints.append(Endpoint(row[0], row[1], row[2], row[3]))
            except re.error as e:
                # Invalid regex will be ignored
                logger.warning(e)
                continue
        return endpoints

    def assureMetricsTable(self):
        """Check if metrics table is present and a hypertable. If not, create one."""

        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        self.conn.commit()
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {METRICS_TABLE_NAME} (
                time TIMESTAMP NOT NULL PRIMARY KEY,
                endpoint_id integer REFERENCES {ENDPOINTS_TABLE_NAME}(endpoint_id),
                duration REAL NOT NULL,
                statusCode INT,
                regexMatch BOOLEAN
            );
        """)
        self.conn.commit()

        # Check if metrics table is a hypertable
        self.cursor.execute(f"""
        SELECT EXISTS (
            SELECT 1 FROM timescaledb_information.hypertables
            WHERE hypertable_name = '{METRICS_TABLE_NAME}'
        );
        """)
        is_hypertable = self.cursor.fetchone()[0]
        if not is_hypertable:
            self.cursor.execute(f"SELECT create_hypertable('{METRICS_TABLE_NAME}', 'time');")
            self.conn.commit()
        return self

    def checkReadiness(self):
        """Ensure DB tables are ready."""
        self.connect2DB()
        self.assureEndpointTable()
        self.assureMetricsTable()
        return self

    def insert(self, metrics: [Stat]):
        """Insert metrics into DB."""
        if len(metrics) == 0:
            return
        # use extras to insert multiple rows
        psycopg2.extras.execute_values(
            self.cursor,
            f"""
            INSERT INTO {ENDPOINTS_TABLE_NAME} (endpoint_id, time, duration, statusCode, regexMatch)
            VALUES %s;
            """,
            [(  stat.endpoint.endpoint_id,
                datetime.fromtimestamp(stat.startTime, timezone.utc),
                stat.duration,
                stat.statusCode,
                stat.regexMatch) for stat in metrics],
            template=None,
            page_size=1000
        )
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()
