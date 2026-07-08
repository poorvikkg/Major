"""
utils.py
--------
Shared, stateless utility functions for the AI pipeline.

Responsibilities:
- Frame persistence (save annotated / raw frames to disk)
- Bounding box format conversions
- Timestamp generation (ISO-8601 UTC)
- Base64 frame encoding for Socket.IO payloads
- Detection result serialization to JSON-safe dicts
- Safe directory creation helpers
"""

import base64
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from pipeline.config import get_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Timestamps
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string: 2024-01-15T10:30:00Z"""
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_now_filename() -> str:
    """Return a filesystem-safe UTC timestamp: 20240115_103000_123456"""
    return utc_now().strftime("%Y%m%d_%H%M%S_%f")


# ---------------------------------------------------------------------------
# Bounding Box Utilities
# ---------------------------------------------------------------------------

def xyxy_to_xywh(box: np.ndarray) -> Dict[str, int]:
    """
    Convert [x1, y1, x2, y2] → {"x": x1, "y": y1, "w": width, "h": height}.

    Parameters
    ----------
    box : (4,) float32 or int array.

    Returns
    -------
    Dict with integer pixel values.
    """
    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
    return {"x": x1, "y": y1, "w": max(0, x2 - x1), "h": max(0, y2 - y1)}


def xyxy_to_dict(box: np.ndarray) -> Dict[str, int]:
    """
    Convert [x1, y1, x2, y2] → {"x1": int, "y1": int, "x2": int, "y2": int}.
    """
    return {
        "x1": int(box[0]),
        "y1": int(box[1]),
        "x2": int(box[2]),
        "y2": int(box[3]),
    }


def box_area(box: np.ndarray) -> int:
    """Return the pixel area of a [x1, y1, x2, y2] bounding box."""
    w = max(0, int(box[2]) - int(box[0]))
    h = max(0, int(box[3]) - int(box[1]))
    return w * h


def scale_box(box: np.ndarray, scale: float) -> np.ndarray:
    """Scale a bounding box by a scalar factor (for resolution changes)."""
    return (box * scale).astype(np.float32)


def crop_box(frame: np.ndarray, box: np.ndarray, pad: int = 0) -> np.ndarray:
    """
    Crop a region from a frame using [x1, y1, x2, y2] coordinates.
    Optional `pad` expands the crop by that many pixels on all sides,
    clamped to frame boundaries.
    """
    h, w = frame.shape[:2]
    x1 = max(0,     int(box[0]) - pad)
    y1 = max(0,     int(box[1]) - pad)
    x2 = min(w - 1, int(box[2]) + pad)
    y2 = min(h - 1, int(box[3]) + pad)
    return frame[y1:y2, x1:x2]


# ---------------------------------------------------------------------------
# Frame / Image I/O
# ---------------------------------------------------------------------------

def save_frame(
    frame: np.ndarray,
    directory: Optional[str] = None,
    filename: Optional[str] = None,
    quality: int = 90,
) -> Optional[str]:
    """
    Save a BGR frame as a JPEG file.

    Parameters
    ----------
    frame     : H × W × 3 uint8 BGR image.
    directory : Output directory path. Defaults to data/uploads/temp/.
    filename  : Custom filename (without extension). Defaults to UTC timestamp.
    quality   : JPEG quality 1–100.

    Returns
    -------
    Absolute path to the saved file, or None on failure.
    """
    out_dir  = Path(directory) if directory else Path(get_config().paths.uploads_temp_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    name     = filename or utc_now_filename()
    filepath = out_dir / f"{name}.jpg"

    try:
        ok = cv2.imwrite(
            str(filepath),
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, quality],
        )
        if not ok:
            logger.error("cv2.imwrite failed for path: %s", filepath)
            return None
        logger.debug("Frame saved: %s", filepath)
        return str(filepath)
    except Exception:
        logger.exception("Error saving frame to %s.", filepath)
        return None


def frame_to_base64(frame: np.ndarray, quality: int = 75) -> str:
    """
    JPEG-encode a BGR frame and return a Base64 string suitable for
    embedding in JSON / Socket.IO events.

    Parameters
    ----------
    frame   : H × W × 3 uint8 BGR image.
    quality : JPEG encode quality (lower = smaller payload).

    Returns
    -------
    Base64-encoded string (without data-URI prefix).
    """
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    ok, buf = cv2.imencode(".jpg", frame, encode_params)
    if not ok:
        logger.error("frame_to_base64: imencode failed — returning empty string.")
        return ""
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def draw_detection(
    frame: np.ndarray,
    box: np.ndarray,
    label: str,
    score: float,
    track_id: Optional[int] = None,
    color: Tuple[int, int, int] = (0, 200, 80),
) -> np.ndarray:
    """
    Draw a single detection (box + label + score) on a copy of the frame.

    Parameters
    ----------
    frame    : H × W × 3 uint8 BGR.
    box      : (4,) [x1, y1, x2, y2] float32.
    label    : Person name or "Unknown".
    score    : Cosine similarity / detection confidence.
    track_id : Optional ByteTrack ID appended to the label.
    color    : BGR color for the box and text.

    Returns
    -------
    Annotated copy of the frame (original is not mutated).
    """
    canvas = frame.copy()
    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])

    # Box
    cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)

    # Label
    tid_suffix = f" #{track_id}" if track_id is not None else ""
    text = f"{label}{tid_suffix} {score:.2f}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    bg_y1 = max(y1 - th - 10, 0)
    cv2.rectangle(canvas, (x1, bg_y1), (x1 + tw + 6, y1), color, -1)
    cv2.putText(
        canvas, text, (x1 + 3, max(y1 - 4, th)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1,
    )
    return canvas


# ---------------------------------------------------------------------------
# Detection result serialization
# ---------------------------------------------------------------------------

def build_detection_payload(
    person_id:    int,
    person_name:  str,
    camera_id:    int,
    score:        float,
    box:          np.ndarray,
    track_id:     Optional[int],
    frame:        Optional[np.ndarray] = None,
    frame_path:   Optional[str]        = None,
    include_frame: bool                = False,
) -> Dict[str, Any]:
    """
    Build the canonical detection payload dict used for both the REST POST
    to the Node.js backend and the Socket.IO event emission.

    Parameters
    ----------
    person_id    : DB person primary key.
    person_name  : Display name.
    camera_id    : DB camera primary key.
    score        : Cosine similarity score [0, 1].
    box          : [x1, y1, x2, y2] detection box.
    track_id     : ByteTrack ID (may be None for video uploads).
    frame        : Raw BGR frame (used only when include_frame=True).
    frame_path   : Path to the saved frame JPEG on disk.
    include_frame: If True, embed Base64-encoded JPEG in the payload.

    Returns
    -------
    JSON-serializable dict.
    """
    payload: Dict[str, Any] = {
        "person_id":   person_id,
        "person_name": person_name,
        "camera_id":   camera_id,
        "score":       round(float(score), 4),
        "confidence":  f"{score * 100:.1f}%",
        "bounding_box": xyxy_to_dict(box),
        "track_id":    track_id,
        "timestamp":   utc_now_iso(),
        "frame_path":  frame_path,
    }
    if include_frame and frame is not None:
        payload["frame_b64"] = frame_to_base64(frame)

    return payload


# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def ensure_dirs(*paths: str) -> None:
    """Create all specified directories (including parents) if they don't exist."""
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def clean_temp_frames(directory: Optional[str] = None, max_age_seconds: int = 3600) -> int:
    """
    Delete JPEG files in the temp directory older than `max_age_seconds`.

    Returns the number of files deleted.
    """
    out_dir  = Path(directory) if directory else Path(get_config().paths.uploads_temp_dir)
    deleted  = 0
    now      = time.time()

    if not out_dir.exists():
        return 0

    for f in out_dir.glob("*.jpg"):
        try:
            if now - f.stat().st_mtime > max_age_seconds:
                f.unlink()
                deleted += 1
        except OSError:
            pass

    if deleted:
        logger.info("Cleaned %d stale frame(s) from %s.", deleted, out_dir)
    return deleted
