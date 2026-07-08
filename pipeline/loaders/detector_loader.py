"""
detector_loader.py
------------------
Singleton lazy-loader for the SCRFD face detector.

Guarantees:
- The ONNX session is created at most once per process lifetime.
- Subsequent calls to get_detector() return the cached FaceDetector instance.
- Thread-safe initialization via threading.Lock.
- Model path and inference config are resolved from pipeline_config.json.
"""

import logging
import threading
from pathlib import Path
from typing import Optional

import onnxruntime as ort

from pipeline.services.detection.detector import FaceDetector
from pipeline.config import get_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton state (private)
# ---------------------------------------------------------------------------
_lock:     threading.Lock          = threading.Lock()
_instance: Optional[FaceDetector]  = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_detector(
    model_path:     Optional[str]   = None,
    conf_threshold: Optional[float] = None,
    nms_threshold:  Optional[float] = None,
) -> FaceDetector:
    """
    Return the singleton FaceDetector, creating it on the first call.

    The ONNX session is built once and reused for every subsequent call,
    which avoids expensive model loading on every request.

    Parameters
    ----------
    model_path      : Override for the ONNX model file path.
                      Defaults to the path in pipeline_config.json.
    conf_threshold  : Detection confidence threshold (only used on first init).
    nms_threshold   : NMS IoU threshold (only used on first init).

    Returns
    -------
    Singleton FaceDetector instance.

    Raises
    ------
    FileNotFoundError  : If the model file does not exist.
    RuntimeError       : If ONNX Runtime fails to build the session.
    """
    global _instance

    if _instance is not None:
        logger.debug("DetectorLoader: returning cached FaceDetector instance.")
        return _instance

    with _lock:
        # Double-checked locking: re-check after acquiring the lock
        if _instance is not None:
            return _instance

        cfg = get_config().detector
        resolved_path = Path(model_path) if model_path else Path(cfg.model_path)

        if not resolved_path.exists():
            raise FileNotFoundError(
                f"[DetectorLoader] SCRFD model not found at '{resolved_path}'. "
                "Download the model and place it under models/face_detection/."
            )

        logger.info(
            "[DetectorLoader] First load — building ONNX session from '%s'.",
            resolved_path,
        )

        session = _build_ort_session(resolved_path, cfg.intra_op_num_threads)
        _instance = FaceDetector(
            model_path     = str(resolved_path),
            conf_threshold = conf_threshold if conf_threshold is not None else cfg.conf_threshold,
            nms_threshold  = nms_threshold  if nms_threshold  is not None else cfg.nms_threshold,
            session        = session,
        )
        logger.info(
            "[DetectorLoader] FaceDetector singleton ready | providers=%s.",
            _instance._session.get_providers(),
        )

    return _instance


def reset_detector() -> None:
    """
    Destroy the singleton instance.

    Useful in test teardown or when hot-swapping a model at runtime.
    After calling this, the next get_detector() call will re-create the instance.
    """
    global _instance
    with _lock:
        _instance = None
    logger.warning("[DetectorLoader] Singleton reset — next call will reload the model.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_ort_session(model_path: Path, num_threads: int) -> ort.InferenceSession:
    """
    Build an optimized ONNX Runtime session with GPU → CPU fallback.
    """
    opts = ort.SessionOptions()
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    opts.intra_op_num_threads = num_threads
    opts.log_severity_level = 3   # suppress verbose ORT logs

    available  = ort.get_available_providers()
    preferred  = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    providers  = [p for p in preferred if p in available] or ["CPUExecutionProvider"]

    logger.debug("[DetectorLoader] ORT providers selected: %s", providers)

    try:
        return ort.InferenceSession(
            str(model_path), sess_options=opts, providers=providers
        )
    except Exception as cuda_exc:
        if "CUDAExecutionProvider" in providers:
            logger.warning(
                "[DetectorLoader] CUDA init failed (%s) — retrying with CPU.", cuda_exc
            )
            return ort.InferenceSession(
                str(model_path),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
        raise
