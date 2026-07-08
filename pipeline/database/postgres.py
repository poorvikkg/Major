"""
pipeline/database/postgres.py
-----------------------------
Backward-compatibility shim.

The PostgreSQL repositories have been refactored into:
    pipeline/database/postgres/

This file re-exports PostgresRepository.
"""

from pipeline.database.postgres.postgres import PostgresRepository

__all__ = ["PostgresRepository"]
