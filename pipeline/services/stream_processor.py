"""
pipeline/services/stream_processor.py
-------------------------------------
Backward-compatibility shim.

The stream processing functionality has been refactored into:
    pipeline/services/camera/

This file re-exports StreamProcessor and its models.
"""

from pipeline.services.camera.stream_processor import StreamProcessor
from pipeline.services.camera.models import StreamConfig, StreamState

__all__ = ["StreamProcessor", "StreamConfig", "StreamState"]
