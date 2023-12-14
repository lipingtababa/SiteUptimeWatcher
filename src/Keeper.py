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

from utils import logger, KEEPER_SLEEP_INTERVAL, RUNNING_STATUS
from metrics import Stat
from endpoint import Endpoint

ENDPOINTS_TABLE_NAME = 'endpoints'
METRICS_TABLE_NAME = 'metrics'

class Keeper:
    """
    This class deals with the database.
    """
    def __init__(self, metrics_buffer: Queue):
        self.connect_to_db()
        self.metrics_buffer = metrics_buffer

    async def run(self):
        """ Consume stats from statsBuffer and insert them into DB."""
        logger.info("A keeper started")
        while RUNNING_STATUS:
            queue_size = self.metrics_buffer.qsize()
            metrics = []
            consumer_length = queue_size if queue_size < 1000 else 1000
            logger.info(f"Keeper consumes {consumer_length}")
            for _ in range(consumer_length):
                # TODO There must be a better way
                # to consume multiple items from a queue
                metric = await self.metrics_buffer.get()
                metrics.append(metric)
                self.metrics_buffer.task_done()
            self.insert_metrics(metrics)
            await asyncio.sleep(KEEPER_SLEEP_INTERVAL)
        logger.info("Exiting a Keeper loop")

    def connect_to_db(self):
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

    def assure_endpoint_table(self):
        """Check if endpoint table is present"""
        self.cursor.execute(
            f"""SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = '{ENDPOINTS_TABLE_NAME}');
            """
            )
        present = self.cursor.fetchone()[0]
        if not present:
            self.cursor.execute(
                f"DROP SEQUENCE IF EXISTS {ENDPOINTS_TABLE_NAME}_endpoint_id_seq CASCADE;"
                )
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {ENDPOINTS_TABLE_NAME} (
                    endpoint_id SERIAL PRIMARY KEY,
                    url VARCHAR(255) not null,
                    regex VARCHAR(255),
                    interval INT CHECK (interval >= 5 AND interval <= 300)
                    );
                """)
            self.conn.commit()
        return self

    def fetch_endpoints(self):
        """Fetch URLs to be monitored from a DB table."""
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

    def assure_metrics_table(self):
        """Check if metrics table is present and a hypertable. If not, create one."""

        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        self.conn.commit()
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {METRICS_TABLE_NAME} (
                start_time TIMESTAMP NOT NULL PRIMARY KEY,
                endpoint_id integer REFERENCES {ENDPOINTS_TABLE_NAME}(endpoint_id),
                duration REAL NOT NULL,
                status_code INT,
                regex_match BOOLEAN
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
            self.cursor.execute(f"SELECT create_hypertable('{METRICS_TABLE_NAME}', 'start_time');")
            self.conn.commit()
        return self

    def check_readiness(self):
        """Ensure DB tables are ready."""
        self.connect_to_db()
        self.assure_endpoint_table()
        self.assure_metrics_table()
        return self

    def insert_metrics(self, metrics: [Stat]):
        """Insert metrics into DB."""
        if len(metrics) == 0:
            return
        # use extras to insert multiple rows
        psycopg2.extras.execute_values(
            self.cursor,
            f"""
            INSERT INTO {METRICS_TABLE_NAME}
            (start_time, endpoint_id, duration, status_code, regex_match)
            VALUES %s;
            """,
            [(  datetime.fromtimestamp(metric.start_time, timezone.utc),
                metric.endpoint.endpoint_id,
                metric.duration,
                metric.status_code,
                metric.regex_match) for metric in metrics],
            template=None,
            page_size=1000
        )
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()
