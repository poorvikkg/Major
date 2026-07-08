"""
pipeline/database/__init__.py
Exposes the primary interfaces of the database layer.
"""

from pipeline.database.connection import get_connection, get_pool, health_check, close_pool
from pipeline.database.postgres import PostgresRepository

__all__ = [
    "get_connection",
    "get_pool",
    "health_check",
    "close_pool",
    "PostgresRepository",
]
