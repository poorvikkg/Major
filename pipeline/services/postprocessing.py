"""
postprocessing.py
-----------------
Production-ready postprocessing utilities for the face recognition pipeline.

Responsibilities:
- Decode raw SCRFD ONNX outputs → bounding boxes + landmarks
- Apply Non-Maximum Suppression (NMS)
- Normalize and L2-embed ArcFace 512-d embeddings
- Map detection coordinates back from letterboxed space to original image space
- Helper: cosine similarity between embeddings

Design: All functions are stateless pure transforms — no model state held here.
"""

import logging
from typing import List, Tuple, Optional

import cv2
import numpy as np

from pipeline.services.recognition.similarity import (
    normalize_embedding,
    cosine_similarity,
    batch_cosine_similarity,
)

logger = logging.getLogger(__name__)

__all__ = [
    "decode_scrfd_outputs",
    "clip_boxes",
    "normalize_embedding",
    "cosine_similarity",
    "batch_cosine_similarity",
]


# ---------------------------------------------------------------------------
# SCRFD anchor / stride constants
# ---------------------------------------------------------------------------

# Strides used by SCRFD-10GF model
_SCRFD_STRIDES: List[int] = [8, 16, 32]

# Number of anchors per location per stride
_NUM_ANCHORS: int = 2


# ---------------------------------------------------------------------------
# Public API — Detector
# ---------------------------------------------------------------------------

def decode_scrfd_outputs(
    raw_outputs: List[np.ndarray],
    input_size: Tuple[int, int],
    conf_threshold: float = 0.5,
    nms_threshold: float = 0.4,
    scale: float = 1.0,
    offset: Tuple[int, int] = (0, 0),
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Decode the raw SCRFD ONNX model outputs into bounding boxes and landmarks.

    SCRFD-10G outputs 9 tensors interleaved as:
        [scores_8, scores_16, scores_32,
         boxes_8,  boxes_16,  boxes_32,
         kps_8,    kps_16,    kps_32]

    Parameters
    ----------
    raw_outputs    : list of 9 numpy arrays from ONNX Runtime.
    input_size     : (width, height) fed into the model (e.g. 640x640).
    conf_threshold : minimum face score to keep.
    nms_threshold  : IoU threshold for NMS.
    scale          : letterbox scale factor (from preprocessing).
    offset         : (pad_left, pad_top) letterbox offsets.

    Returns
    -------
    boxes      : (N, 4) float32 — [x1, y1, x2, y2] in original image coords.
    scores     : (N,)   float32 — confidence scores.
    landmarks  : (N, 5, 2) float32 — 5-pt landmarks in original image coords.
    """
    if len(raw_outputs) != 9:
        raise ValueError(
            f"Expected 9 output tensors from SCRFD, got {len(raw_outputs)}."
        )

    iw, ih = input_size
    all_boxes: List[np.ndarray] = []
    all_scores: List[np.ndarray] = []
    all_landmarks: List[np.ndarray] = []

    pad_left, pad_top = offset

    for idx, stride in enumerate(_SCRFD_STRIDES):
        score_tensor = raw_outputs[idx]                      # (1, H*W*A, 1)
        box_tensor   = raw_outputs[idx + 3]                 # (1, H*W*A, 4)
        kps_tensor   = raw_outputs[idx + 6]                 # (1, H*W*A, 10)

        score_tensor = score_tensor.squeeze(0)              # (H*W*A, 1)
        box_tensor   = box_tensor.squeeze(0)                # (H*W*A, 4)
        kps_tensor   = kps_tensor.squeeze(0)                # (H*W*A, 10)

        scores_flat = score_tensor[:, 0]

        # Generate anchor center grid
        fh = (ih + stride - 1) // stride
        fw = (iw + stride - 1) // stride
        anchor_centers = _generate_anchor_centers(fh, fw, stride)

        # Keep only high-confidence detections
        keep_mask = scores_flat >= conf_threshold
        if not np.any(keep_mask):
            continue

        scores_kept = scores_flat[keep_mask]
        boxes_kept  = box_tensor[keep_mask]
        kps_kept    = kps_tensor[keep_mask]
        centers     = anchor_centers[keep_mask]

        # Decode boxes: dist2bbox
        x1 = centers[:, 0] - boxes_kept[:, 0] * stride
        y1 = centers[:, 1] - boxes_kept[:, 1] * stride
        x2 = centers[:, 0] + boxes_kept[:, 2] * stride
        y2 = centers[:, 1] + boxes_kept[:, 3] * stride
        decoded_boxes = np.stack([x1, y1, x2, y2], axis=-1)

        # Decode landmarks
        decoded_kps = _decode_landmarks(kps_kept, centers, stride)

        all_boxes.append(decoded_boxes)
        all_scores.append(scores_kept)
        all_landmarks.append(decoded_kps)

    if not all_boxes:
        return (
            np.empty((0, 4),    dtype=np.float32),
            np.empty((0,),      dtype=np.float32),
            np.empty((0, 5, 2), dtype=np.float32),
        )

    boxes     = np.concatenate(all_boxes,     axis=0)
    scores    = np.concatenate(all_scores,    axis=0)
    landmarks = np.concatenate(all_landmarks, axis=0)

    # NMS
    nms_idx = _nms(boxes, scores, nms_threshold)
    boxes     = boxes[nms_idx]
    scores    = scores[nms_idx]
    landmarks = landmarks[nms_idx]

    # Map from letterboxed space back to original image coordinates
    boxes, landmarks = _unletterbox(boxes, landmarks, scale, pad_left, pad_top)

    return boxes.astype(np.float32), scores.astype(np.float32), landmarks.astype(np.float32)


def clip_boxes(
    boxes: np.ndarray,
    image_shape: Tuple[int, int],
) -> np.ndarray:
    """
    Clip bounding boxes to be within image boundaries.

    Parameters
    ----------
    boxes       : (N, 4) float32 [x1, y1, x2, y2].
    image_shape : (height, width) of the original image.

    Returns
    -------
    Clipped boxes of shape (N, 4).
    """
    h, w = image_shape
    boxes = boxes.copy()
    boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, w)
    boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, h)
    return boxes


# ---------------------------------------------------------------------------
# Public API — Recognizer (Re-exported for backward compatibility)
# ---------------------------------------------------------------------------
# normalize_embedding, cosine_similarity, and batch_cosine_similarity 
# have been moved to pipeline.services.recognition.similarity


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _generate_anchor_centers(
    fh: int,
    fw: int,
    stride: int,
) -> np.ndarray:
    """
    Generate anchor center coordinates for one SCRFD feature-map stride.

    Returns
    -------
    (fh * fw * _NUM_ANCHORS, 2) float32 [cx, cy].
    """
    y, x = np.mgrid[:fh, :fw]
    centers = np.stack([x, y], axis=-1).reshape(-1, 2).astype(np.float32)
    centers = (centers + 0.5) * stride
    # Repeat for _NUM_ANCHORS anchors per location
    centers = np.repeat(centers, _NUM_ANCHORS, axis=0)
    return centers


def _decode_landmarks(
    kps: np.ndarray,
    centers: np.ndarray,
    stride: int,
) -> np.ndarray:
    """
    Decode landmark offsets from SCRFD into absolute pixel coordinates.

    Parameters
    ----------
    kps     : (N, 10) raw landmark deltas (x0, y0, x1, y1, ..., x4, y4).
    centers : (N, 2) anchor center positions [cx, cy].
    stride  : feature-map stride.

    Returns
    -------
    (N, 5, 2) decoded landmark coordinates.
    """
    n = kps.shape[0]
    decoded = np.zeros((n, 5, 2), dtype=np.float32)
    for i in range(5):
        decoded[:, i, 0] = centers[:, 0] + kps[:, i * 2]     * stride
        decoded[:, i, 1] = centers[:, 1] + kps[:, i * 2 + 1] * stride
    return decoded


def _nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_threshold: float,
) -> np.ndarray:
    """
    Batched Non-Maximum Suppression using OpenCV's NMSBoxes.

    Returns indices of kept detections sorted by descending score.
    """
    if boxes.shape[0] == 0:
        return np.array([], dtype=np.int32)

    # OpenCV NMSBoxes expects [x, y, w, h]
    xywh = boxes.copy()
    xywh[:, 2] -= xywh[:, 0]
    xywh[:, 3] -= xywh[:, 1]

    indices = cv2.dnn.NMSBoxes(
        bboxes=xywh.tolist(),
        scores=scores.tolist(),
        score_threshold=0.0,
        nms_threshold=iou_threshold,
    )
    if indices is None or len(indices) == 0:
        return np.array([], dtype=np.int32)

    return np.array(indices).flatten()


def _unletterbox(
    boxes: np.ndarray,
    landmarks: np.ndarray,
    scale: float,
    pad_left: int,
    pad_top: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove letterbox padding and scale coordinates back to original image space.
    """
    if scale <= 0:
        raise ValueError(f"Invalid scale factor: {scale}")

    # Boxes
    boxes[:, 0] = (boxes[:, 0] - pad_left) / scale
    boxes[:, 1] = (boxes[:, 1] - pad_top)  / scale
    boxes[:, 2] = (boxes[:, 2] - pad_left) / scale
    boxes[:, 3] = (boxes[:, 3] - pad_top)  / scale

    # Landmarks
    landmarks[:, :, 0] = (landmarks[:, :, 0] - pad_left) / scale
    landmarks[:, :, 1] = (landmarks[:, :, 1] - pad_top)  / scale

    return boxes, landmarks
