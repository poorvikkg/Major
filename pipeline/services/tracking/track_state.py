"""
track_state.py
--------------
Purpose  : Data models for the face tracking system.
           Defines the Track lifecycle states and the Track data container.
Inputs   : Raw detection data (box, score, landmarks).
Outputs  : Track objects consumed by FaceTracker.
Raises   : N/A — pure data model, no I/O.

Single Responsibility: state definition and data modeling ONLY.
No algorithm, no I/O, no Kalman math lives here.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

import numpy as np


class TrackState(Enum):
    """
    Lifecycle states for a tracked face.

    Active  — track is confirmed and currently matched to a detection.
    Lost    — no detection matched this frame; kept alive up to max_age.
    Removed — aged out; will be deleted from the registry.
    """
    Active  = auto()
    Lost    = auto()
    Removed = auto()


@dataclass
class Track:
    """
    A single tracked face with a stable integer ID.

    Attributes
    ----------
    track_id            : Globally unique integer assigned at birth.
    state               : Current lifecycle state.
    box                 : Most recent bounding box [x1, y1, x2, y2] float32.
    score               : Most recent detection confidence [0, 1].
    landmarks           : Most recent 5-point facial landmarks (5, 2) float32.
    age                 : Total frames since this track was created.
    hits                : Frames this track was successfully matched.
    frames_since_update : Frames elapsed since last successful match.
    _kalman             : Internal Kalman filter (set by FaceTracker).
    """
    track_id:            int
    state:               TrackState
    box:                 np.ndarray    # (4,) float32
    score:               float
    landmarks:           np.ndarray    # (5, 2) float32
    age:                 int           = 0
    hits:                int           = 0
    frames_since_update: int           = 0
    _kalman:             Any           = field(default=None, repr=False)

    def mark_updated(
        self,
        box:       np.ndarray,
        score:     float,
        landmarks: np.ndarray,
    ) -> None:
        """
        Apply a matched detection to this track.

        Purpose  : Update state after a successful detection association.
        Inputs   : box, score, landmarks from the matched DetectionResult.
        Outputs  : Mutates self in-place.
        """
        self.box                 = box
        self.score               = score
        self.landmarks           = landmarks
        self.hits               += 1
        self.frames_since_update = 0
        self.state               = TrackState.Active
        if self._kalman is not None:
            self._kalman.update(box)

    def advance(self) -> None:
        """
        Advance one frame (predict without a detection match).

        Purpose  : Increment counters and propagate Kalman state forward.
        Inputs   : None.
        Outputs  : Mutates self in-place; updates box from Kalman prediction.
        """
        self.age                += 1
        self.frames_since_update += 1
        if self._kalman is not None:
            predicted = self._kalman.predict()
            self.box  = predicted.astype(np.float32)
