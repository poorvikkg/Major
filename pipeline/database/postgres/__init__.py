"""
pipeline/database/postgres/__init__.py
Public API for the postgres sub-package.
"""

from pipeline.database.postgres.postgres import PostgresRepository

__all__ = ["PostgresRepository"]
