"""
pipeline/services/video/__init__.py
Public API for the video sub-package.
"""

from pipeline.services.video.video_processor import VideoProcessor
from pipeline.services.video.detection_report import DetectionReport, VideoDetection
from pipeline.services.video.video_deduplicator import VideoDeduplicator

__all__ = [
    "VideoProcessor",
    "DetectionReport",
    "VideoDetection",
    "VideoDeduplicator",
]
