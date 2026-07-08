"""
recognizer_loader.py
--------------------
Singleton lazy-loader for the ArcFace R100 face recognizer.

Guarantees:
- The ONNX session is created at most once per process lifetime.
- Subsequent calls to get_recognizer() return the cached FaceRecognizer instance.
- Thread-safe initialization via threading.Lock.
- Model path is resolved from pipeline_config.json.
"""

import logging
import threading
from pathlib import Path
from typing import Optional

import onnxruntime as ort

from pipeline.services.recognition.recognizer import FaceRecognizer
from pipeline.services.recognition.embedding_extractor import EmbeddingExtractor
from pipeline.config import get_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton state (private)
# ---------------------------------------------------------------------------
_lock:     threading.Lock                = threading.Lock()
_instance: Optional[EmbeddingExtractor]  = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_recognizer(model_path: Optional[str] = None) -> EmbeddingExtractor:
    """
    Return the singleton EmbeddingExtractor, creating it on the first call.

    The underlying ONNX session is built once and shared across all callers.
    Thread-safe double-checked locking is used to ensure a single build even
    under concurrent access.

    Parameters
    ----------
    model_path : Override for the ONNX model file path.
                 Defaults to the path in pipeline_config.json.

    Returns
    -------
    Singleton EmbeddingExtractor instance.

    Raises
    ------
    FileNotFoundError  : If the model file does not exist.
    RuntimeError       : If ONNX Runtime fails to build the session.
    """
    global _instance

    if _instance is not None:
        logger.debug("RecognizerLoader: returning cached EmbeddingExtractor instance.")
        return _instance

    with _lock:
        if _instance is not None:
            return _instance

        cfg = get_config().recognizer
        resolved_path = Path(model_path) if model_path else Path(cfg.model_path)

        if not resolved_path.exists():
            raise FileNotFoundError(
                f"[RecognizerLoader] ArcFace model not found at '{resolved_path}'. "
                "Place the fine-tuned ONNX file under models/face_recognition/."
            )

        logger.info(
            "[RecognizerLoader] First load — building ONNX session from '%s'.",
            resolved_path,
        )

        session = _build_ort_session(resolved_path, cfg.intra_op_num_threads)
        recognizer = FaceRecognizer(
            model_path=str(resolved_path),
            session=session,
        )
        _instance = EmbeddingExtractor(recognizer)
        logger.info(
            "[RecognizerLoader] EmbeddingExtractor singleton ready | providers=%s.",
            recognizer._session.get_providers(),
        )

    return _instance


def reset_recognizer() -> None:
    """
    Destroy the singleton instance.

    Useful in test teardown or when swapping to a newly fine-tuned model.
    """
    global _instance
    with _lock:
        _instance = None
    logger.warning(
        "[RecognizerLoader] Singleton reset — next call will reload the model."
    )


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

    available = ort.get_available_providers()
    preferred = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    providers = [p for p in preferred if p in available] or ["CPUExecutionProvider"]

    logger.debug("[RecognizerLoader] ORT providers selected: %s", providers)

    try:
        return ort.InferenceSession(
            str(model_path), sess_options=opts, providers=providers
        )
    except Exception as cuda_exc:
        if "CUDAExecutionProvider" in providers:
            logger.warning(
                "[RecognizerLoader] CUDA init failed (%s) — retrying with CPU.", cuda_exc
            )
            return ort.InferenceSession(
                str(model_path),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
        raise
