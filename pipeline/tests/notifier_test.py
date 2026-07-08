"""
notifier_test.py
----------------
Unit tests for the Notifier service.
"""

import unittest
from unittest.mock import MagicMock
import numpy as np

from pipeline.services.notification.notifier import Notifier


class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.http_client = MagicMock()
        self.socket_client = MagicMock()
        self.db_repo = MagicMock()
        
        self.notifier = Notifier(
            http_client=self.http_client,
            socket_client=self.socket_client,
            db_repo=self.db_repo,
            cooldown_sec=30,
            save_frames=False,
        )

    def test_notify_success(self):
        box = np.array([10, 10, 100, 100], dtype=np.float32)
        
        result = self.notifier.notify(
            person_id=42,
            person_name="John Doe",
            camera_id=1,
            score=0.95,
            box=box,
            track_id=5,
            frame=None,
        )
        
        self.assertTrue(result)
        self.http_client.post_detection.assert_called_once()
        self.socket_client.emit_detection.assert_called_once()
        self.db_repo.insert_detection_log.assert_called_once()

    def test_notify_cooldown(self):
        box = np.array([10, 10, 100, 100], dtype=np.float32)
        
        # First notification should succeed
        res1 = self.notifier.notify(42, "John Doe", 1, 0.95, box)
        self.assertTrue(res1)
        
        # Second notification immediately after should be suppressed by cooldown
        res2 = self.notifier.notify(42, "John Doe", 1, 0.95, box)
        self.assertFalse(res2)
        
        # Verify that HTTP post was only called once
        self.assertEqual(self.http_client.post_detection.call_count, 1)

    def test_reset_cooldown(self):
        box = np.array([10, 10, 100, 100], dtype=np.float32)
        
        self.notifier.notify(42, "John Doe", 1, 0.95, box)
        self.notifier.reset_cooldown(42, 1)
        
        # Should succeed again after manual reset
        res2 = self.notifier.notify(42, "John Doe", 1, 0.95, box)
        self.assertTrue(res2)


if __name__ == "__main__":
    unittest.main()
