"""
detection_result.py
-------------------
Purpose  : Immutable data container for a single detected face.
Inputs   : Raw bounding box, confidence score, and landmarks.
Outputs  : DetectionResult object.
Raises   : N/A.

Single Responsibility: Data modeling ONLY.
No model loading, inference, or processing logic lives here.
"""

from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass(frozen=True)
class DetectionResult:
    """Immutable container for a single detected face."""
    box: np.ndarray          # (4,) float32 [x1, y1, x2, y2]
    score: float             # Confidence in [0, 1]
    landmarks: np.ndarray    # (5, 2) float32 pixel coordinates

    @property
    def area(self) -> float:
        w = float(self.box[2] - self.box[0])
        h = float(self.box[3] - self.box[1])
        return max(0.0, w * h)

    @property
    def xyxy(self) -> Tuple[int, int, int, int]:
        return (
            int(self.box[0]), int(self.box[1]),
            int(self.box[2]), int(self.box[3]),
        )
