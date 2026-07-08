"""
tracker_loader.py
-----------------
Purpose : Singleton per-stream factory for FaceTracker instances.
          Each video stream needs its own tracker state (track IDs, Kalman
          states) — this registry ensures one instance per stream_id.
Inputs  : stream_id string + optional override parameters.
Outputs : FaceTracker instance (created once, cached forever per stream_id).
Raises  : N/A.

Config-driven defaults are read from pipeline.config (tracker section).
This module is thread-safe at the registry level;
each FaceTracker itself is NOT thread-safe by design.
"""

import logging
import threading
from typing import Dict

# Canonical import from the new tracking sub-package
from pipeline.services.tracking.tracker import FaceTracker
from pipeline.config import get_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level registry
# ---------------------------------------------------------------------------
_lock:     threading.Lock              = threading.Lock()
_registry: Dict[str, FaceTracker]     = {}

_DEFAULT_STREAM_ID = "__default__"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_tracker(
    stream_id:        str            = _DEFAULT_STREAM_ID,
    max_age:          int            = None,
    min_hits:         int            = None,
    iou_threshold:    float          = None,
    high_conf_thresh: float          = None,
    low_conf_thresh:  float          = None,
) -> FaceTracker:
    """
    Return the FaceTracker instance for the given stream_id.

    Purpose  : Return a cached per-stream tracker, creating it on first call.
    Inputs   : stream_id        — unique stream identifier.
               max_age          — override config tracker.max_age.
               min_hits         — override config tracker.min_hits.
               iou_threshold    — override config tracker.iou_threshold.
               high_conf_thresh — override config tracker.high_conf_thresh.
               low_conf_thresh  — override config tracker.low_conf_thresh.
    Outputs  : FaceTracker instance for this stream.
    Raises   : N/A.
    """
    if stream_id in _registry:
        logger.debug("TrackerLoader: cached tracker for stream='%s'.", stream_id)
        return _registry[stream_id]

    with _lock:
        if stream_id in _registry:   # double-checked lock
            return _registry[stream_id]

        cfg     = get_config().tracker
        tracker = FaceTracker(
            max_age          = max_age          if max_age          is not None else cfg.max_age,
            min_hits         = min_hits         if min_hits         is not None else cfg.min_hits,
            iou_threshold    = iou_threshold    if iou_threshold    is not None else cfg.iou_threshold,
            high_conf_thresh = high_conf_thresh if high_conf_thresh is not None else cfg.high_conf_thresh,
            low_conf_thresh  = low_conf_thresh  if low_conf_thresh  is not None else cfg.low_conf_thresh,
        )
        _registry[stream_id] = tracker
        logger.info("TrackerLoader: FaceTracker created for stream='%s'.", stream_id)

    return tracker


def get_default_tracker(**kwargs) -> FaceTracker:
    """
    Convenience wrapper — return the default single-stream tracker.

    Equivalent to calling get_tracker(stream_id='__default__', **kwargs).
    """
    return get_tracker(stream_id=_DEFAULT_STREAM_ID, **kwargs)


def release_tracker(stream_id: str) -> bool:
    """
    Remove and reset the tracker for a specific stream.

    Call this when a video stream ends to free memory and prevent stale
    track IDs from leaking into the next session.

    Parameters
    ----------
    stream_id : The stream identifier originally passed to get_tracker().

    Returns
    -------
    True if a tracker was found and removed, False if stream_id was unknown.
    """
    with _lock:
        tracker = _registry.pop(stream_id, None)
        if tracker is not None:
            tracker.reset()
            logger.info(
                "[TrackerLoader] Tracker for stream='%s' released.", stream_id
            )
            return True
        logger.warning(
            "[TrackerLoader] release_tracker called for unknown stream='%s'.", stream_id
        )
        return False


def release_all_trackers() -> int:
    """
    Reset and remove all registered tracker instances.

    Returns
    -------
    Number of trackers released.
    """
    with _lock:
        count = len(_registry)
        for tracker in _registry.values():
            tracker.reset()
        _registry.clear()
    logger.warning("[TrackerLoader] All %d tracker(s) released.", count)
    return count


def list_active_streams() -> list:
    """
    Return a snapshot of all stream IDs that currently have a tracker instance.
    """
    with _lock:
        return list(_registry.keys())
