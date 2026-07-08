"""
pipeline/services/video_processor.py
------------------------------------
Backward-compatibility shim.

The video processing functionality has been refactored into:
    pipeline/services/video/

This file re-exports VideoProcessor and its models.
"""

from pipeline.services.video.video_processor import VideoProcessor
from pipeline.services.video.detection_report import DetectionReport, VideoDetection

__all__ = ["VideoProcessor", "DetectionReport", "VideoDetection"]
