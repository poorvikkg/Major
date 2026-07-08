"""
database_test.py
----------------
Unit tests for PostgresRepository.
"""

import unittest
from unittest.mock import MagicMock, patch

from pipeline.database.postgres import PostgresRepository


class TestPostgresRepository(unittest.TestCase):
    def setUp(self):
        # Create a mock connection factory that yields a mock cursor
        self.mock_cursor = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        
        self.mock_conn_factory = MagicMock()
        self.mock_conn_factory.return_value.__enter__.return_value = self.mock_conn

        self.repo = PostgresRepository(connection_factory=self.mock_conn_factory)

    def test_get_all_missing_persons(self):
        self.mock_cursor.fetchall.return_value = [{"id": 1, "name": "John Doe"}]
        result = self.repo.get_all_missing_persons()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "John Doe")

    def test_get_camera_by_id(self):
        self.mock_cursor.fetchone.return_value = {"id": 2, "name": "Main Gate"}
        result = self.repo.get_camera_by_id(2)
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 2)
        self.assertEqual(result["name"], "Main Gate")

    def test_get_camera_not_found(self):
        self.mock_cursor.fetchone.return_value = None
        result = self.repo.get_camera_by_id(999)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
