"""
connection.py
-------------
PostgreSQL connection pool manager for the AI pipeline database layer.

Responsibilities:
- Build and own a psycopg2 connection pool (thread-safe ThreadedConnectionPool).
- Expose a context-manager for acquiring / releasing connections safely.
- Read all credentials from environment variables — no secrets in code.
- Implement singleton pattern: one pool per process lifetime.
- Provide a health-check helper used by startup probes.

Environment variables required (match your backend .env):
    DB_HOST     — PostgreSQL host          (default: localhost)
    DB_PORT     — PostgreSQL port          (default: 5432)
    DB_NAME     — Database name
    DB_USER     — Database user
    DB_PASSWORD — Database password
    DB_MIN_CONN — Min pool connections    (default: 2)
    DB_MAX_CONN — Max pool connections    (default: 10)
"""

import logging
import os
import threading
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2 import pool as pg_pool
from psycopg2.extensions import connection as PgConnection

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton state
# ---------------------------------------------------------------------------
_lock:         threading.Lock                              = threading.Lock()
_pool:         Optional[pg_pool.ThreadedConnectionPool]     = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_pool() -> pg_pool.ThreadedConnectionPool:
    """
    Return the singleton connection pool, initializing it on first call.

    Raises
    ------
    psycopg2.OperationalError  : If the database is unreachable.
    EnvironmentError           : If required env vars are missing.
    """
    global _pool
    if _pool is not None:
        return _pool

    with _lock:
        if _pool is not None:
            return _pool

        config = _build_config()
        logger.info(
            "Creating PostgreSQL pool | host=%s:%s | db=%s | pool=[%d..%d]",
            config["host"], config["port"], config["dbname"],
            config["minconn"], config["maxconn"],
        )
        _pool = pg_pool.ThreadedConnectionPool(
            minconn=config.pop("minconn"),
            maxconn=config.pop("maxconn"),
            **config,
        )
        logger.info("PostgreSQL connection pool created.")

    return _pool


@contextmanager
def get_connection() -> Generator[PgConnection, None, None]:
    """
    Context manager that acquires a connection from the pool and returns it
    after the block exits (even on exception).

    Usage
    -----
    >>> with get_connection() as conn:
    ...     with conn.cursor() as cur:
    ...         cur.execute("SELECT 1")
    """
    p = get_pool()
    conn: Optional[PgConnection] = None
    try:
        conn = p.getconn()
        conn.autocommit = False
        yield conn
    except Exception:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn is not None:
            p.putconn(conn)


def health_check() -> bool:
    """
    Execute a lightweight query to verify database connectivity.

    Returns True if successful, False on any error.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        logger.debug("Database health check passed.")
        return True
    except Exception:
        logger.exception("Database health check FAILED.")
        return False


def close_pool() -> None:
    """
    Close all connections in the pool and destroy the singleton.
    Call during application shutdown.
    """
    global _pool
    with _lock:
        if _pool is not None:
            _pool.closeall()
            _pool = None
            logger.info("PostgreSQL connection pool closed.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_config() -> dict:
    """
    Read database configuration from environment variables.

    Raises
    ------
    EnvironmentError : If DB_NAME, DB_USER, or DB_PASSWORD are missing.
    """
    required = {"DB_NAME": "dbname", "DB_USER": "user", "DB_PASSWORD": "password"}
    cfg: dict = {}

    for env_key, cfg_key in required.items():
        value = os.environ.get(env_key, "").strip()
        if not value:
            raise EnvironmentError(
                f"Required environment variable '{env_key}' is not set. "
                "Ensure your .env file is loaded before starting the pipeline."
            )
        cfg[cfg_key] = value

    cfg["host"]    = os.environ.get("DB_HOST", "localhost").strip()
    cfg["port"]    = int(os.environ.get("DB_PORT", "5432"))
    cfg["minconn"] = int(os.environ.get("DB_MIN_CONN", "2"))
    cfg["maxconn"] = int(os.environ.get("DB_MAX_CONN", "10"))

    return cfg
