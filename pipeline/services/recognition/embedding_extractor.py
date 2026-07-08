"""
embedding_extractor.py
----------------------
Purpose  : Extract normalized embeddings from BGR face crops.
Inputs   : 112x112 uint8 BGR face crops + FaceRecognizer instance.
Outputs  : (N, 512) L2-normalized float32 embeddings.
Raises   : N/A (returns None/zeros on invalid input).

Single Responsibility: Batching, validation, and normalization logic.
Delegates inference to FaceRecognizer and math to similarity.py.
"""

import logging
from typing import List, Optional

import numpy as np

from pipeline.services.preprocessing import normalize_for_recognizer
from pipeline.services.recognition.recognizer import FaceRecognizer
from pipeline.services.recognition.similarity import normalize_embedding

logger = logging.getLogger(__name__)

_EMBEDDING_DIM = 512


class EmbeddingExtractor:
    """
    Stateless extractor wrapping a FaceRecognizer.
    """

    def __init__(self, recognizer: FaceRecognizer) -> None:
        self._recognizer = recognizer

    def get_embedding(self, face_crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract a single L2-normalized 512-d embedding.

        Parameters
        ----------
        face_crop : 112 x 112 x 3 uint8 BGR aligned face image.

        Returns
        -------
        (512,) float32 L2-normalized embedding, or None if inference fails.
        """
        if not self._validate_crop(face_crop, context="get_embedding"):
            return None

        try:
            blob = normalize_for_recognizer(face_crop)        # (1, 3, 112, 112)
            raw  = self._recognizer.run_inference(blob)       # (1, 512)
            embedding = normalize_embedding(raw[0])           # (512,)
            logger.debug(
                "Embedding extracted | norm=%.6f",
                float(np.linalg.norm(embedding)),
            )
            return embedding
        except Exception:
            logger.exception("Error in get_embedding — returning None.")
            return None

    def get_embeddings_batch(
        self,
        face_crops: List[np.ndarray],
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        Extract L2-normalized embeddings from multiple face crops efficiently.
        """
        n = len(face_crops)
        if n == 0:
            return np.empty((0, _EMBEDDING_DIM), dtype=np.float32)

        results = np.zeros((n, _EMBEDDING_DIM), dtype=np.float32)

        valid_indices: List[int]        = []
        valid_blobs:   List[np.ndarray] = []

        for i, crop in enumerate(face_crops):
            if self._validate_crop(crop, context=f"batch[{i}]"):
                valid_indices.append(i)
                valid_blobs.append(normalize_for_recognizer(crop).squeeze(0))  # (3,112,112)
            else:
                logger.warning("Batch index %d has invalid crop — using zero embedding.", i)

        if not valid_blobs:
            return results

        # Process in mini-batches
        for start in range(0, len(valid_blobs), batch_size):
            end   = min(start + batch_size, len(valid_blobs))
            batch = np.stack(valid_blobs[start:end], axis=0)        # (B, 3, 112, 112)
            try:
                raw_batch = self._recognizer.run_inference(batch)    # (B, 512)
                for j, raw in enumerate(raw_batch):
                    global_idx = valid_indices[start + j]
                    results[global_idx] = normalize_embedding(raw)
            except Exception:
                logger.exception(
                    "Error in batch inference [%d:%d] — embeddings set to zero.", start, end
                )

        logger.debug(
            "Batch embedding complete | n=%d valid=%d", n, len(valid_indices)
        )
        return results

    @staticmethod
    def _validate_crop(crop: np.ndarray, context: str = "") -> bool:
        """
        Return True if the crop is a valid 112x112 BGR uint8 image.
        """
        if crop is None or not isinstance(crop, np.ndarray):
            logger.warning("[%s] crop is None or not ndarray.", context)
            return False
        if crop.ndim != 3 or crop.shape[2] != 3:
            logger.warning("[%s] Expected H x W x 3 image, got %s.", context, crop.shape)
            return False
        if crop.size == 0:
            logger.warning("[%s] Empty crop.", context)
            return False
        return True
