"""This module deals with the database and endpoint management.
1. Ensure DB is ready
2. Fetch sites from DB
3. CRUD operations for endpoints
"""
from typing import List, Optional, Dict, Any
import os
import re
import psycopg2
import psycopg2.extras

from src.utils import logger
from src.endpoint import Endpoint

ENDPOINTS_TABLE_NAME = 'endpoints'

class EndpointManager:
    """
    This class deals with the database and endpoint management.
    """
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT")
            )

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

    def fetch_all_endpoints(self) -> List[Endpoint]:
        """Fetch all endpoints from the database."""
        endpoints = []
        conn = self.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""SELECT endpoint_id, url, regex, interval FROM 
                    {ENDPOINTS_TABLE_NAME};"""
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

    def get_endpoint(self, endpoint_id: int) -> Optional[Endpoint]:
        """Get a specific endpoint by ID."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""SELECT endpoint_id, url, regex, interval FROM 
                    {ENDPOINTS_TABLE_NAME} 
                    WHERE endpoint_id = %s;""",
                    (endpoint_id,)
                    )
                row = cursor.fetchone()
                if row:
                    return Endpoint(row[0], row[1], row[2], row[3])
                return None
        except Exception as e:
            logger.error(e)
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)

    def create_endpoint(self, url: str, regex: Optional[str], interval: int) -> Endpoint:
        """Create a new endpoint."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""INSERT INTO {ENDPOINTS_TABLE_NAME} (url, regex, interval)
                    VALUES (%s, %s, %s)
                    RETURNING endpoint_id, url, regex, interval;""",
                    (url, regex, interval)
                    )
                row = cursor.fetchone()
                conn.commit()
                return Endpoint(row[0], row[1], row[2], row[3])
        except Exception as e:
            logger.error(e)
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)

    def update_endpoint(self, endpoint_id: int, update_data: Dict[str, Any]) -> Endpoint:
        """Update an existing endpoint."""
        if not update_data:
            return self.get_endpoint(endpoint_id)

        conn = self.get_connection()
        try:
            # Build the SET clause dynamically based on provided fields
            set_clauses = []
            values = []
            for key, value in update_data.items():
                set_clauses.append(f"{key} = %s")
                values.append(value)
            values.append(endpoint_id)  # Add endpoint_id for WHERE clause

            with conn.cursor() as cursor:
                cursor.execute(
                    f"""UPDATE {ENDPOINTS_TABLE_NAME}
                    SET {', '.join(set_clauses)}
                    WHERE endpoint_id = %s
                    RETURNING endpoint_id, url, regex, interval;""",
                    tuple(values)
                    )
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Endpoint with ID {endpoint_id} not found")
                conn.commit()
                return Endpoint(row[0], row[1], row[2], row[3])
        except Exception as e:
            logger.error(e)
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)

    def delete_endpoint(self, endpoint_id: int) -> None:
        """Delete an endpoint."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""DELETE FROM {ENDPOINTS_TABLE_NAME}
                    WHERE endpoint_id = %s;""",
                    (endpoint_id,)
                    )
                if cursor.rowcount == 0:
                    raise ValueError(f"Endpoint with ID {endpoint_id} not found")
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
        return self

    def __del__(self):
        self.connection_pool.closeall()
