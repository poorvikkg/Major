"""
tracker.py
----------
Purpose  : ByteTrack-style multi-face tracker orchestrator.
           Manages track lifecycle: spawn, update, age, remove.
Inputs   : List[DetectionResult] per frame from FaceDetector.
Outputs  : List[Track] — confirmed active tracks after each update.
Raises   : N/A.

Single Responsibility: track lifecycle orchestration ONLY.
All math is delegated to iou_utils, association, and kalman_filter.
Configuration is loaded from pipeline.config via TrackerConfig.

One FaceTracker instance must be created per video stream.
Not thread-safe by design — protect with a lock at the stream level.
"""

import logging
from typing import Dict, List, Set, Tuple

import numpy as np

from pipeline.services.tracking.track_state  import Track, TrackState
from pipeline.services.tracking.kalman_filter import KalmanBoxTracker
from pipeline.services.tracking.iou_utils    import compute_iou
from pipeline.services.tracking.association  import greedy_match, unmatched_indices

logger = logging.getLogger(__name__)


class FaceTracker:
    """
    ByteTrack-inspired multi-face tracker.

    Two-pass association strategy:
      Pass 1 — high-confidence detections  vs. Active tracks.
      Pass 2 — remaining low-confidence    vs. Lost tracks.

    Parameters
    ----------
    max_age          : Frames a Lost track survives before deletion.
    min_hits         : Detection hits required before a track is reported.
    iou_threshold    : Minimum IoU to accept a detection–track pair.
    high_conf_thresh : Score threshold separating pass-1 / pass-2 detections.
    low_conf_thresh  : Minimum score to use a detection at all.
    """

    def __init__(
        self,
        max_age:          int   = 30,
        min_hits:         int   = 3,
        iou_threshold:    float = 0.3,
        high_conf_thresh: float = 0.6,
        low_conf_thresh:  float = 0.1,
    ) -> None:
        self._max_age          = max_age
        self._min_hits         = min_hits
        self._iou_threshold    = iou_threshold
        self._high_conf_thresh = high_conf_thresh
        self._low_conf_thresh  = low_conf_thresh

        self._tracks:      Dict[int, Track] = {}
        self._next_id:     int              = 1
        self._frame_count: int              = 0

        logger.info(
            "FaceTracker ready | max_age=%d | min_hits=%d | iou=%.2f",
            max_age, min_hits, iou_threshold,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, detections: List) -> List[Track]:
        """
        Advance the tracker by one frame.

        Purpose  : Run two-pass association, age unmatched tracks, spawn
                   new tracks for unmatched high-confidence detections.
        Inputs   : detections — List of DetectionResult (box, score, landmarks).
        Outputs  : Sorted list of confirmed active Track objects.
        """
        self._frame_count += 1
        self._predict_all()

        high_dets = [d for d in detections if d.score >= self._high_conf_thresh]
        low_dets  = [d for d in detections if self._low_conf_thresh <= d.score < self._high_conf_thresh]

        active = self._by_state(TrackState.Active)
        lost   = self._by_state(TrackState.Lost)

        matched_ids, unmatched_high = self._associate(high_dets, active)
        self._associate(low_dets, lost)
        self._age_unmatched({t.track_id for t in active} - matched_ids)

        for det in unmatched_high:
            self._spawn(det)

        self._prune_removed()
        return self._confirmed_tracks()

    def reset(self) -> None:
        """
        Reset all tracker state.

        Purpose  : Call between unrelated video streams or after a camera restart.
        Inputs   : None.
        Outputs  : Mutates self — clears all tracks and counters.
        """
        self._tracks.clear()
        self._next_id    = 1
        self._frame_count = 0
        logger.debug("FaceTracker reset.")

    @property
    def active_track_ids(self) -> List[int]:
        """Sorted IDs of tracks currently in Active state."""
        return sorted(
            t.track_id for t in self._tracks.values()
            if t.state == TrackState.Active
        )

    @property
    def frame_count(self) -> int:
        """Total frames processed since last reset."""
        return self._frame_count

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _predict_all(self) -> None:
        """Advance all tracks forward by one frame (Kalman predict)."""
        for track in self._tracks.values():
            track.advance()

    def _by_state(self, state: TrackState) -> List[Track]:
        return [t for t in self._tracks.values() if t.state == state]

    def _associate(
        self,
        detections: List,
        tracks: List[Track],
    ) -> Tuple[Set[int], List]:
        """
        Greedily match detections to tracks via IoU cost matrix.

        Purpose  : Run one pass of the two-pass ByteTrack association.
        Inputs   : detections — candidate DetectionResult list.
                   tracks     — candidate Track list.
        Outputs  : (matched_track_ids, unmatched_detections).
        """
        if not detections or not tracks:
            return set(), detections

        det_boxes   = np.stack([d.box for d in detections])
        trk_boxes   = np.stack([t.box for t in tracks])
        iou_mat     = compute_iou(det_boxes, trk_boxes)
        pairs       = greedy_match(1.0 - iou_mat)

        matched_ids: Set[int] = set()
        matched_di:  Set[int] = set()

        for di, ti in pairs:
            if iou_mat[di, ti] < self._iou_threshold:
                continue
            tracks[ti].mark_updated(
                detections[di].box,
                detections[di].score,
                detections[di].landmarks,
            )
            matched_ids.add(tracks[ti].track_id)
            matched_di.add(di)

        unmatched = [d for i, d in enumerate(detections) if i not in matched_di]
        return matched_ids, unmatched

    def _age_unmatched(self, track_ids: Set[int]) -> None:
        """Mark unmatched Active tracks as Lost or Removed based on age."""
        for tid in track_ids:
            t = self._tracks[tid]
            if t.frames_since_update > self._max_age:
                t.state = TrackState.Removed
            else:
                t.state = TrackState.Lost

    def _spawn(self, detection) -> None:
        """Create a new Track for an unmatched high-confidence detection."""
        kalman = KalmanBoxTracker(detection.box)
        track  = Track(
            track_id  = self._next_id,
            state     = TrackState.Active,
            box       = detection.box.copy(),
            score     = detection.score,
            landmarks = detection.landmarks.copy(),
            hits      = 1,
            _kalman   = kalman,
        )
        self._tracks[self._next_id] = track
        self._next_id += 1

    def _prune_removed(self) -> None:
        self._tracks = {
            k: v for k, v in self._tracks.items()
            if v.state != TrackState.Removed
        }

    def _confirmed_tracks(self) -> List[Track]:
        return sorted(
            [t for t in self._tracks.values()
             if t.state == TrackState.Active and t.hits >= self._min_hits],
            key=lambda t: t.track_id,
        )
