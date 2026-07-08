"""
tracking_service.py
-------------------
Tracking service layer.

Wraps the tracker_loader registry and FaceTracker with business logic:
- Provides named stream tracking contexts
- Returns serializable track state for API consumers
- Abstracts tracker reset / stream lifecycle from CameraManager

Design: thin facade — all heavy logic stays in tracker.py.
"""

import logging
from typing import Dict, List, Optional

from pipeline.services.tracker       import FaceTracker, Track, TrackState
from pipeline.loaders.tracker_loader import get_tracker, release_tracker, list_active_streams

logger = logging.getLogger(__name__)


class TrackingService:
    """
    Manages named tracker instances for multiple concurrent streams.

    Parameters
    ----------
    max_age          : Frames before a lost track is deleted.
    min_hits         : Minimum detections before a track is confirmed.
    iou_threshold    : IoU threshold for association.
    """

    def __init__(
        self,
        max_age:       int   = 30,
        min_hits:      int   = 3,
        iou_threshold: float = 0.3,
    ) -> None:
        self._max_age       = max_age
        self._min_hits      = min_hits
        self._iou_threshold = iou_threshold
        logger.info(
            "TrackingService initialised | max_age=%d | min_hits=%d | iou=%.2f",
            max_age, min_hits, iou_threshold,
        )

    def get_tracker(self, stream_id: str) -> FaceTracker:
        """
        Return (or create) a FaceTracker for the given stream.

        Parameters
        ----------
        stream_id : Unique identifier for the video stream.
        """
        return get_tracker(
            stream_id=stream_id,
            max_age=self._max_age,
            min_hits=self._min_hits,
            iou_threshold=self._iou_threshold,
        )

    def release_stream(self, stream_id: str) -> bool:
        """
        Release and reset the tracker for a stream that has ended.

        Returns
        -------
        True if found and released, False otherwise.
        """
        return release_tracker(stream_id)

    def get_active_stream_ids(self) -> List[str]:
        """Return IDs of all streams with an active tracker instance."""
        return list_active_streams()

    def get_track_summary(self, stream_id: str) -> Dict:
        """
        Return a JSON-serializable summary of the current track state
        for a given stream.

        Returns
        -------
        {
            "stream_id": str,
            "frame_count": int,
            "active_track_ids": List[int],
            "track_count": int,
        }
        """
        tracker = get_tracker(stream_id)
        return {
            "stream_id":        stream_id,
            "frame_count":      tracker.frame_count,
            "active_track_ids": tracker.active_track_ids,
            "track_count":      len(tracker.active_track_ids),
        }

    @staticmethod
    def tracks_to_dicts(tracks: List[Track]) -> List[Dict]:
        """
        Convert a list of Track objects to JSON-serializable dicts.

        Used by API endpoints that expose tracking state.
        """
        result = []
        for t in tracks:
            result.append({
                "track_id":  t.track_id,
                "state":     t.state.name,
                "score":     round(t.score, 4),
                "hits":      t.hits,
                "age":       t.age,
                "box": {
                    "x1": int(t.box[0]),
                    "y1": int(t.box[1]),
                    "x2": int(t.box[2]),
                    "y2": int(t.box[3]),
                },
            })
        return result
