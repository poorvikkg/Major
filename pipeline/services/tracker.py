"""
pipeline/services/tracker.py
-----------------------------
Backward-compatibility shim.

The tracking implementation has been refactored into:
    pipeline/services/tracking/

This file re-exports all public symbols so that existing imports
such as `from pipeline.services.tracker import FaceTracker` continue
to work without modification.

New code should import directly from the sub-package:
    from pipeline.services.tracking import FaceTracker, Track, TrackState
"""

# Re-export tracking public API
from pipeline.services.tracking.track_state   import Track, TrackState          # noqa: F401
from pipeline.services.tracking.kalman_filter import KalmanBoxTracker            # noqa: F401
from pipeline.services.tracking.iou_utils    import compute_iou as _iou         # noqa: F401
from pipeline.services.tracking.association  import greedy_match                 # noqa: F401
from pipeline.services.tracking.tracker      import FaceTracker                  # noqa: F401

__all__ = [
    "FaceTracker",
    "Track",
    "TrackState",
    "KalmanBoxTracker",
    "_iou",          # keep old private name for any test that may reference it
    "greedy_match",
]
