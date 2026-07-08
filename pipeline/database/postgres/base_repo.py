"""
base_repo.py
------------
Base repository class with connection management and serialization.
"""

from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Dict, Generator, Optional
from uuid import UUID

import psycopg2
import psycopg2.extras

from pipeline.database.connection import get_connection

ConnectionFactory = Callable[[], Any]


class BaseRepository:
    def __init__(self, connection_factory: Optional[ConnectionFactory] = None):
        self._conn_factory = connection_factory or get_connection

    @contextmanager
    def _connect(self) -> Generator:
        with self._conn_factory() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                try:
                    yield cur
                except psycopg2.Error:
                    conn.rollback()
                    raise

    @staticmethod
    def _serialize_row(row: Any) -> Dict:
        result: Dict = {}
        for key, value in dict(row).items():
            if isinstance(value, (datetime, date)):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, UUID):
                result[key] = str(value)
            else:
                result[key] = value
        return result
