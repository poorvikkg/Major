"""
pipeline/services/camera/__init__.py
Public API for the camera stream sub-package.
"""

from pipeline.services.camera.camera_manager import CameraManager
from pipeline.services.camera.stream_processor import StreamProcessor
from pipeline.services.camera.models import StreamConfig, StreamState

__all__ = [
    "CameraManager",
    "StreamProcessor",
    "StreamConfig",
    "StreamState",
]
