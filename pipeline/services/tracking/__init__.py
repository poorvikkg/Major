"""
pipeline/services/tracking/__init__.py
Public API for the tracking sub-package.
"""

from pipeline.services.tracking.track_state  import Track, TrackState
from pipeline.services.tracking.tracker      import FaceTracker
from pipeline.services.tracking.iou_utils    import compute_iou
from pipeline.services.tracking.association  import greedy_match
from pipeline.services.tracking.kalman_filter import KalmanBoxTracker

__all__ = [
    "Track",
    "TrackState",
    "FaceTracker",
    "compute_iou",
    "greedy_match",
    "KalmanBoxTracker",
]
