"""
pipeline/services/detector.py
-----------------------------
Backward-compatibility shim.

The detection implementation has been refactored into:
    pipeline/services/detection/

This file re-exports all public symbols so that existing imports
such as `from pipeline.services.detector import FaceDetector, DetectionResult`
continue to work without modification.

New code should import directly from the sub-package:
    from pipeline.services.detection import FaceDetector, DetectionResult
"""

from pipeline.services.detection.detector import FaceDetector
from pipeline.services.detection.detection_result import DetectionResult

__all__ = [
    "FaceDetector",
    "DetectionResult",
]
