"""
face_image_processor.py
-----------------------
Purpose  : Process a single image from disk to extract a face embedding.
Inputs   : Image file path, FaceDetector, EmbeddingExtractor.
Outputs  : L2-normalized 512-d embedding.
Raises   : N/A (returns None on failure).

Single Responsibility: Pipeline orchestration for a single static image.
"""

import logging
from typing import Optional

import cv2
import numpy as np

from pipeline.services.detection.detector import FaceDetector
from pipeline.services.recognition.embedding_extractor import EmbeddingExtractor

logger = logging.getLogger(__name__)


def embed_from_path(
    image_path: str,
    detector: FaceDetector,
    extractor: EmbeddingExtractor,
) -> Optional[np.ndarray]:
    """
    Load an image, detect the largest face, align it, and return its embedding.
    Returns None on any failure.
    """
    try:
        frame = cv2.imread(image_path)
        if frame is None:
            logger.warning("Cannot read image: %s", image_path)
            return None

        results = detector.detect_faces(frame)
        if not results:
            logger.warning("No face detected in: %s", image_path)
            return None

        # Use the largest-area face
        best = max(results, key=lambda r: r.area)
        crops = detector.get_aligned_crops(frame, [best])
        if not crops:
            logger.warning("Alignment failed for: %s", image_path)
            return None

        embedding = extractor.get_embedding(crops[0])
        if embedding is None:
            logger.warning("Embedding extraction failed for: %s", image_path)
            return None

        return embedding

    except Exception:
        logger.exception("Unexpected error processing image: %s", image_path)
        return None
