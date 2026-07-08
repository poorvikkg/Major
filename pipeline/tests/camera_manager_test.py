"""
camera_manager_test.py
----------------------
Unit tests for the CameraManager.
"""

import unittest
from unittest.mock import MagicMock, patch

from pipeline.services.camera_manager import CameraManager


class TestCameraManager(unittest.TestCase):
    def setUp(self):
        self.inference = MagicMock()
        self.db_repo = MagicMock()
        self.notifier = MagicMock()
        self.socket_client = MagicMock()
        
        self.manager = CameraManager(
            inference=self.inference,
            db_repo=self.db_repo,
            notifier=self.notifier,
            socket_client=self.socket_client,
        )

    def test_start_and_stop_camera(self):
        # Mocking the stream processor to avoid actual threads
        with patch("pipeline.services.camera.camera_manager.StreamProcessor") as mock_processor:
            mock_processor_instance = mock_processor.return_value
            mock_processor_instance.start.return_value = True
            
            # Start camera
            result = self.manager.start_camera(camera_id=1, stream_url="rtsp://mock")
            self.assertTrue(result)
            
            # Verify state
            self.assertTrue(self.manager.is_camera_active(1))
            self.assertIn(1, self.manager.get_active_cameras())
            
            # Stop camera
            self.manager.stop_camera(1)
            self.assertFalse(self.manager.is_camera_active(1))
            self.assertNotIn(1, self.manager.get_active_cameras())

    def test_stop_unknown_camera(self):
        result = self.manager.stop_camera(999)
        self.assertFalse(result)

    def test_stop_all(self):
        with patch("pipeline.services.camera.camera_manager.StreamProcessor"):
            self.manager.start_camera(1, "rtsp://mock1")
            self.manager.start_camera(2, "rtsp://mock2")
            
            self.assertEqual(len(self.manager.get_active_cameras()), 2)
            
            self.manager.stop_all()
            
            self.assertEqual(len(self.manager.get_active_cameras()), 0)


if __name__ == "__main__":
    unittest.main()
