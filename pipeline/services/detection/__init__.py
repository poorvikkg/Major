"""
pipeline/services/detection/__init__.py
Public API for the detection sub-package.
"""

from pipeline.services.detection.detection_result import DetectionResult
from pipeline.services.detection.detector import FaceDetector

__all__ = [
    "DetectionResult",
    "FaceDetector",
]
