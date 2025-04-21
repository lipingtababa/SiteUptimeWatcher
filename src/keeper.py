"""This module deals with the database.
1. Ensure DB is ready
2. Fetch sites from DB
3. Insert stats into DB
4. Send metrics to Datakit
"""
import os
from datetime import datetime, timezone
import re
from typing import List

from asyncio import Queue
import asyncio
import psycopg2
import psycopg2.extras
import psycopg2.pool
import requests

from utils import logger, KEEPER_SLEEP_INTERVAL, RUNNING_STATUS
from metrics import Stat
from endpoint import Endpoint

ENDPOINTS_TABLE_NAME = 'endpoints'
METRICS_TABLE_NAME = 'metrics'
PG_BATCH_SIZE = 1000

# Datakit configuration
DATAKIT_ENABLED = os.getenv("DATAKIT_ENABLED", "true") == "true"
datakit_host = os.getenv("DATAKIT_HOST", "localhost")
datakit_port = int(os.getenv("DATAKIT_PORT", "9529"))
datakit_url = f"http://{datakit_host}:{datakit_port}"

class Keeper:
    """
    This class deals with the database.
    """
    def __init__(self, metrics_buffer: Queue):
        self.metrics_buffer = metrics_buffer
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT")
            )

    async def run(self):
        """ Consume stats from metrics_buffer and insert them into DB."""
        # log the keeper's id
        logger.info(f"Keeper {id(self)} started")
        while RUNNING_STATUS:
            try:
                queue_size = self.metrics_buffer.qsize()
                if queue_size > 0:
                    metrics = []
                    consumer_length = queue_size if queue_size < PG_BATCH_SIZE else PG_BATCH_SIZE
                    logger.info(f"Keeper consumes {consumer_length}")
                    for _ in range(consumer_length):
                        # TODO There must be a better way
                        # to consume multiple items from a queue
                        metric = await self.metrics_buffer.get()
                        metrics.append(metric)
                        self.metrics_buffer.task_done()
                    self.insert_metrics(metrics)
                    # Send metrics to Datakit if enabled
                    if DATAKIT_ENABLED:
                        self._send_metrics_to_datakit(metrics)
            except Exception as e:
                logger.error(e)
            finally:
                await asyncio.sleep(KEEPER_SLEEP_INTERVAL)
        logger.info("Exiting a Keeper loop")

    def get_connection(self):
        """Get a connection from the pool."""
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        """Release a connection back to the pool."""
        self.connection_pool.putconn(conn)

    def assure_endpoint_table(self):
        """Check if endpoint table is present"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = '{ENDPOINTS_TABLE_NAME}');
                    """
                    )
                present = cursor.fetchone()[0]
                if not present:
                    cursor.execute(
                        f"DROP SEQUENCE IF EXISTS {ENDPOINTS_TABLE_NAME}_endpoint_id_seq CASCADE;"
                        )
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {ENDPOINTS_TABLE_NAME} (
                            endpoint_id SERIAL PRIMARY KEY,
                            url VARCHAR(255) not null,
                            regex VARCHAR(255),
                            interval INT CHECK (interval >= 5 AND interval <= 300)
                            );
                        """)
                    conn.commit()
        except Exception as e:
            logger.error(e)
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)

    def fetch_endpoints(self, partition_count: int, partition_id: int):
        """Fetch URLs to be monitored from a DB table.
        Multiple instances of this program can be run to utilize multiple cores.
        Each instance will fetch a different set of URLs.
        """
        endpoints = []
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""SELECT endpoint_id, url, regex, interval FROM 
                    {ENDPOINTS_TABLE_NAME} 
                    where endpoint_id % {partition_count} = {partition_id};"""
                    )
                rows = cursor.fetchall()
                for row in rows:
                    try:
                        endpoints.append(Endpoint(row[0], row[1], row[2], row[3]))
                    except re.error as e:
                        # Invalid regex will be ignored
                        logger.warning(e)
                        continue
        except Exception as e:
            logger.error(e)
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)
        return endpoints

    def assure_metrics_table(self):
        """Check if metrics table is present and a hypertable. If not, create one."""

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {METRICS_TABLE_NAME} (
                        start_time TIMESTAMP NOT NULL,
                        endpoint_id integer REFERENCES {ENDPOINTS_TABLE_NAME}(endpoint_id),
                        duration REAL NOT NULL,
                        status_code INT,
                        regex_match BOOLEAN,
                        PRIMARY KEY (start_time, endpoint_id)
                    );
                """)

                # Check if metrics table is a hypertable
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM timescaledb_information.hypertables
                        WHERE hypertable_name = '{METRICS_TABLE_NAME}'
                    );
                    """)
                is_hypertable = cursor.fetchone()[0]
                if not is_hypertable:
                    cursor.execute(f"SELECT create_hypertable('{METRICS_TABLE_NAME}', 'start_time');")
                conn.commit()
        except Exception as e:
            logger.error(e)
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)

    def check_readiness(self):
        """Ensure DB tables are ready."""
        self.assure_endpoint_table()
        self.assure_metrics_table()
        return self

    def insert_metrics(self, metrics: [Stat]):
        """Insert metrics into DB."""
        if len(metrics) == 0:
            return
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # use extras to insert multiple rows
                psycopg2.extras.execute_values(
                    cursor,
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
                    page_size=PG_BATCH_SIZE
                )
                conn.commit()
        except Exception as e:
            logger.error(e)
            conn.rollback()
        finally:
            self.release_connection(conn)

    def _send_metrics_to_datakit(self, metrics: List[Stat]):
        """Send metrics to DataKit using HTTP API.
        DataKit expects metrics in the following format:
        {
            "measurement": "site_uptime_watcher",
            "tags": {
                "endpoint": "url",
                "status_code": "code",
                "regex_match": "true/false"
            },
            "fields": {
                "response_time": value,
                "status_code": value,
                "regex_match": 1/0
            }
        }
        """
        try:
            # Prepare metrics data for all metrics in the batch
            metrics_data = []
            for metric in metrics:
                # Create tags for the metrics
                tags = {
                    "endpoint": metric.endpoint.url,
                    "status_code": str(metric.status_code),
                    "regex_match": str(metric.regex_match).lower()
                }
                # Add metrics data
                metrics_data.append({
                    "measurement": "site_uptime_watcher",
                    "tags": tags,
                    "fields": {
                        "response_time": metric.duration,
                        "status_code": metric.status_code,
                        "regex_match": 1 if metric.regex_match else 0
                    }
                })
            # Send metrics via HTTP API
            metrics_url = f"{datakit_url}/v1/write/metrics"
            response = requests.post(metrics_url, json=metrics_data, timeout=5)
            if response.status_code != 200:
                logger.error(f"Error sending metrics to DataKit: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error sending metrics to DataKit: {e}")

    def __del__(self):
        self.connection_pool.closeall()
