"""
preprocessing.py
----------------
Production-ready preprocessing utilities for the face recognition pipeline.

Responsibilities:
- Image normalization for SCRFD detector
- Image normalization for ArcFace recognizer (112x112 RGB)
- Face alignment via landmark-based affine transform
- Safe frame resizing while preserving aspect ratio
- Dtype/channel validation and coercion

Design: All functions are stateless pure transforms — no model state is held here.
"""

import logging
from typing import Tuple, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SCRFD detector normalization constants (ImageNet mean/std in BGR order)
# ---------------------------------------------------------------------------
_DETECTOR_MEAN = np.array([127.5, 127.5, 127.5], dtype=np.float32)
_DETECTOR_STD  = np.array([128.0, 128.0, 128.0], dtype=np.float32)

# ---------------------------------------------------------------------------
# ArcFace reference 5-point landmarks (112 x 112 space)
# ---------------------------------------------------------------------------
ARCFACE_DST = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_for_detector(
    image: np.ndarray,
    target_size: Tuple[int, int] = (640, 640),
) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """
    Resize and normalize a BGR image for the SCRFD ONNX model.

    Parameters
    ----------
    image       : H x W x 3  uint8 BGR frame from OpenCV.
    target_size : (width, height) expected by the model (default 640 x 640).

    Returns
    -------
    blob   : float32 NCHW tensor ready for inference.
    scale  : resize scale factor (to map detections back to original space).
    offset : (pad_left, pad_top) pixel offsets introduced by letterbox padding.
    """
    image = _ensure_bgr_uint8(image)
    resized, scale, offset = _letterbox(image, target_size)

    blob = resized.astype(np.float32)
    blob = (blob - _DETECTOR_MEAN) / _DETECTOR_STD        # HWC → normalize
    blob = np.transpose(blob, (2, 0, 1))                   # HWC → CHW
    blob = np.expand_dims(blob, axis=0)                    # CHW → NCHW
    return blob, scale, offset


def normalize_for_recognizer(face_crop: np.ndarray) -> np.ndarray:
    """
    Prepare a 112 x 112 aligned face crop for ArcFace ONNX inference.

    Converts BGR → RGB, normalizes to [-1, 1], and returns a float32
    NCHW tensor of shape (1, 3, 112, 112).

    Parameters
    ----------
    face_crop : 112 x 112 x 3 uint8 BGR image.

    Returns
    -------
    blob : float32 NCHW tensor.
    """
    if face_crop.shape[:2] != (112, 112):
        logger.debug(
            "face_crop shape %s ≠ (112, 112) — resizing.", face_crop.shape[:2]
        )
        face_crop = cv2.resize(face_crop, (112, 112), interpolation=cv2.INTER_LINEAR)

    face_crop = _ensure_bgr_uint8(face_crop)
    rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

    blob = rgb.astype(np.float32)
    blob = (blob - 127.5) / 128.0                         # normalize to [-1, 1]
    blob = np.transpose(blob, (2, 0, 1))                  # HWC → CHW
    blob = np.expand_dims(blob, axis=0)                   # CHW → NCHW
    return blob


def align_face(
    image: np.ndarray,
    landmarks: np.ndarray,
    output_size: Tuple[int, int] = (112, 112),
) -> Optional[np.ndarray]:
    """
    Align a face to the ArcFace canonical 5-point template using a similarity
    (rigid + scale) affine transform estimated from 5 facial landmarks.

    Parameters
    ----------
    image       : full BGR frame.
    landmarks   : array of shape (5, 2) — [left_eye, right_eye, nose,
                  mouth_left, mouth_right] in pixel coordinates.
    output_size : (width, height) of the output crop (default 112 x 112).

    Returns
    -------
    Aligned 112 x 112 BGR crop, or None if estimation fails.
    """
    if landmarks.shape != (5, 2):
        logger.warning(
            "Expected landmarks shape (5, 2), got %s — skipping alignment.",
            landmarks.shape,
        )
        return None

    src = landmarks.astype(np.float32)
    dst = ARCFACE_DST.copy()

    # Scale destination landmarks if output_size ≠ 112 x 112
    if output_size != (112, 112):
        sx = output_size[0] / 112.0
        sy = output_size[1] / 112.0
        dst[:, 0] *= sx
        dst[:, 1] *= sy

    M, inliers = cv2.estimateAffinePartial2D(
        src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.0
    )
    if M is None:
        logger.warning("Affine estimation failed — falling back to direct warp.")
        M, _ = cv2.estimateAffinePartial2D(src, dst)

    if M is None:
        logger.error("Could not estimate affine transform for face alignment.")
        return None

    aligned = cv2.warpAffine(
        image,
        M,
        output_size,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )
    return aligned


def resize_frame(
    frame: np.ndarray,
    max_side: int = 1280,
) -> Tuple[np.ndarray, float]:
    """
    Downscale a frame so its longest side ≤ max_side, preserving aspect ratio.
    Returns the resized frame and the scale factor applied (1.0 if no resize).

    Parameters
    ----------
    frame    : input BGR image.
    max_side : maximum pixel dimension of the longer side.

    Returns
    -------
    (resized_frame, scale)
    """
    h, w = frame.shape[:2]
    longest = max(h, w)
    if longest <= max_side:
        return frame, 1.0

    scale = max_side / longest
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    logger.debug("Frame resized (%d, %d) → (%d, %d), scale=%.4f", w, h, new_w, new_h, scale)
    return resized, scale


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _ensure_bgr_uint8(image: np.ndarray) -> np.ndarray:
    """Coerce an image to uint8 BGR with 3 channels."""
    if image is None or image.size == 0:
        raise ValueError("Received empty or None image.")

    if image.dtype != np.uint8:
        if image.max() <= 1.0:
            image = (image * 255).clip(0, 255).astype(np.uint8)
        else:
            image = image.clip(0, 255).astype(np.uint8)

    if image.ndim == 2:                             # grayscale → BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:  # BGRA → BGR
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif image.ndim == 3 and image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return image


def _letterbox(
    image: np.ndarray,
    target_size: Tuple[int, int],
    color: Tuple[int, int, int] = (0, 0, 0),
) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """
    Letterbox-resize an image to target_size preserving aspect ratio.

    Returns
    -------
    (padded_image, scale, (pad_left, pad_top))
    """
    h, w = image.shape[:2]
    tw, th = target_size

    scale = min(tw / w, th / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    canvas = np.full((th, tw, 3), color, dtype=np.uint8)
    pad_top  = (th - new_h) // 2
    pad_left = (tw - new_w) // 2
    canvas[pad_top : pad_top + new_h, pad_left : pad_left + new_w] = resized

    return canvas, scale, (pad_left, pad_top)
