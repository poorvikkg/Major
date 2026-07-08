"""
iou_utils.py
------------
Purpose  : Pairwise Intersection-over-Union (IoU) computation.
Inputs   : Two (M, 4) and (N, 4) float32 bounding-box arrays [x1, y1, x2, y2].
Outputs  : (M, N) float32 IoU matrix with values in [0, 1].
Raises   : N/A — pure vectorised math, no side effects.

Single Responsibility: IoU math ONLY.
No tracking, no Kalman, no detection logic lives here.
"""

import numpy as np


def compute_iou(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Compute pairwise IoU between two sets of axis-aligned bounding boxes.

    Purpose  : Produce the cost matrix used by the association step.
    Inputs   : a — (M, 4) float32 boxes [x1, y1, x2, y2].
               b — (N, 4) float32 boxes [x1, y1, x2, y2].
    Outputs  : (M, N) float32 IoU values in [0, 1].
    Raises   : N/A.
    """
    if a.shape[0] == 0 or b.shape[0] == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float32)

    area_a = _areas(a)   # (M,)
    area_b = _areas(b)   # (N,)

    inter_x1 = np.maximum(a[:, None, 0], b[None, :, 0])  # (M, N)
    inter_y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    inter_x2 = np.minimum(a[:, None, 2], b[None, :, 2])
    inter_y2 = np.minimum(a[:, None, 3], b[None, :, 3])

    inter_w   = np.maximum(0.0, inter_x2 - inter_x1)
    inter_h   = np.maximum(0.0, inter_y2 - inter_y1)
    inter     = inter_w * inter_h                          # (M, N)

    union = area_a[:, None] + area_b[None, :] - inter
    union = np.maximum(union, 1e-6)
    return (inter / union).astype(np.float32)


def _areas(boxes: np.ndarray) -> np.ndarray:
    """
    Compute pixel area for each box in an (N, 4) array.

    Purpose  : Helper for compute_iou — avoids code duplication.
    Inputs   : boxes — (N, 4) float32.
    Outputs  : (N,) float32 areas (clamped to ≥ 0).
    """
    w = np.maximum(0.0, boxes[:, 2] - boxes[:, 0])
    h = np.maximum(0.0, boxes[:, 3] - boxes[:, 1])
    return w * h
