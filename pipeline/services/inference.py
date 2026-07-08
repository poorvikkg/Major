"""
inference.py
------------
Core inference orchestrator for a single frame.

Responsibilities:
- Combine FaceDetector + FaceRecognizer + FAISSManager into one call
- For each detected face: align → embed → FAISS search → return match
- Return a structured list of InferenceResult objects
- Apply a recognition threshold gate to prevent false positives

Design:
- FaceInference is stateless between frames (no tracker, no stream state).
- Tracker integration happens one layer up (stream_processor / video_processor).
- Dependency-injected: pass your singleton instances so models load only once.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from pipeline.services.detector       import FaceDetector, DetectionResult
from pipeline.services.recognition    import EmbeddingExtractor
from pipeline.services.faiss_manager  import FAISSManager
from pipeline.services.utils          import utc_now_iso, xyxy_to_dict

logger = logging.getLogger(__name__)

# Default cosine similarity threshold — reject matches below this
_DEFAULT_RECOGNITION_THRESHOLD = 0.45


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class InferenceResult:
    """
    Complete per-face inference output for one frame.

    Attributes
    ----------
    person_id   : DB person primary key, or None if unrecognized.
    person_name : Display name from the DB (populated by callers with DB access).
    score       : Cosine similarity score [0, 1] (0 for unknown faces).
    box         : (4,) float32 [x1, y1, x2, y2] in original frame coords.
    landmarks   : (5, 2) float32 facial keypoints.
    embedding   : (512,) float32 L2-normalized embedding for this face.
    timestamp   : ISO-8601 UTC string when inference ran.
    is_match    : True if person_id is not None (score ≥ threshold).
    """
    person_id:   Optional[int]
    person_name: str
    score:       float
    box:         np.ndarray
    landmarks:   np.ndarray
    embedding:   np.ndarray
    timestamp:   str
    is_match:    bool

    @property
    def bounding_box_dict(self) -> Dict[str, int]:
        return xyxy_to_dict(self.box)

    def to_dict(self) -> Dict:
        """JSON-serializable representation (omits numpy arrays)."""
        return {
            "person_id":    self.person_id,
            "person_name":  self.person_name,
            "score":        round(self.score, 4),
            "confidence":   f"{self.score * 100:.1f}%",
            "bounding_box": self.bounding_box_dict,
            "is_match":     self.is_match,
            "timestamp":    self.timestamp,
        }


# ---------------------------------------------------------------------------
# FaceInference
# ---------------------------------------------------------------------------

class FaceInference:
    """
    Single-frame face detection + recognition orchestrator.

    Parameters
    ----------
    detector    : Singleton FaceDetector (SCRFD).
    recognizer  : Singleton FaceRecognizer (ArcFace R100).
    faiss_mgr   : FAISSManager holding the registered persons index.
    threshold   : Minimum cosine similarity to count as a positive match.
    top_k       : Number of FAISS candidates to retrieve per face.
    """

    def __init__(
        self,
        detector:   FaceDetector,
        recognizer: EmbeddingExtractor,
        faiss_mgr:  FAISSManager,
        threshold:  float = _DEFAULT_RECOGNITION_THRESHOLD,
        top_k:      int   = 3,
    ) -> None:
        self._detector   = detector
        self._recognizer = recognizer
        self._faiss      = faiss_mgr
        self._threshold  = threshold
        self._top_k      = top_k
        logger.info(
            "FaceInference ready | threshold=%.2f | top_k=%d", threshold, top_k
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, frame: np.ndarray) -> List[InferenceResult]:
        """
        Run full detection + recognition on one BGR frame.

        Parameters
        ----------
        frame : H × W × 3 uint8 BGR image.

        Returns
        -------
        List of InferenceResult — one per detected face.
        Faces that fail alignment or embedding are silently excluded.
        Empty list if no faces are detected or an error occurs.
        """
        if frame is None or frame.size == 0:
            logger.warning("FaceInference.run: received empty frame.")
            return []

        ts = utc_now_iso()
        t_start = time.perf_counter()

        try:
            detections: List[DetectionResult] = self._detector.detect_faces(frame)
        except Exception:
            logger.exception("Detection failed — returning [].")
            return []

        if not detections:
            return []

        # Align all faces in one pass
        crops = self._detector.get_aligned_crops(frame, detections)

        # Extract embeddings in one batched forward pass
        if len(crops) == 0:
            return []

        embeddings = self._recognizer.get_embeddings_batch(crops)  # (M, 512)

        results: List[InferenceResult] = []

        for i, (det, emb) in enumerate(zip(detections, embeddings)):
            if np.all(emb == 0):          # zero vector = failed embedding
                logger.debug("Zero embedding at index %d — skipping.", i)
                continue

            # FAISS cosine search
            matches = self._faiss.search(
                query_embedding=emb,
                top_k=self._top_k,
                threshold=self._threshold,
            )

            if matches:
                best       = matches[0]
                person_id  = best["person_id"]
                score      = best["score"]
                is_match   = True
            else:
                person_id  = None
                score      = 0.0
                is_match   = False

            results.append(
                InferenceResult(
                    person_id   = person_id,
                    person_name = "",          # populated by caller (needs DB)
                    score       = score,
                    box         = det.box,
                    landmarks   = det.landmarks,
                    embedding   = emb,
                    timestamp   = ts,
                    is_match    = is_match,
                )
            )

        t_end = time.perf_counter()
        logger.debug(
            "FaceInference.run completed in %.1f ms | faces=%d | matches=%d",
            (t_end - t_start) * 1000,
            len(results), sum(1 for r in results if r.is_match),
        )
        return results

    def run_on_crop(self, crop: np.ndarray) -> Optional[InferenceResult]:
        """
        Run recognition on a pre-cropped 112×112 face image.
        Useful when detection has already been performed upstream.

        Returns None if embedding fails or no match is found.
        """
        emb = self._recognizer.get_embedding(crop)
        if emb is None:
            return None

        matches = self._faiss.search(emb, top_k=self._top_k, threshold=self._threshold)

        ts = utc_now_iso()
        if matches:
            best = matches[0]
            return InferenceResult(
                person_id   = best["person_id"],
                person_name = "",
                score       = best["score"],
                box         = np.zeros(4, dtype=np.float32),
                landmarks   = np.zeros((5, 2), dtype=np.float32),
                embedding   = emb,
                timestamp   = ts,
                is_match    = True,
            )
        return None

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, value: float) -> None:
        if not 0 < value < 1:
            raise ValueError(f"Threshold must be in (0, 1), got {value}.")
        self._threshold = value
        logger.info("FaceInference threshold updated to %.2f.", value)
