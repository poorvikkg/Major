"""
similarity.py
-------------
Purpose  : Math operations for comparing and normalizing embeddings.
Inputs   : Raw float32 embeddings (vectors or matrices).
Outputs  : Normalized embeddings or float32 similarity scores.
Raises   : N/A.

Single Responsibility: Cosine similarity math ONLY.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    L2-normalize a 512-d ArcFace embedding vector.

    Parameters
    ----------
    embedding : (512,) or (1, 512) float32 raw embedding.

    Returns
    -------
    Unit-normalized (512,) float32 vector.
    """
    embedding = embedding.flatten().astype(np.float32)
    norm = np.linalg.norm(embedding)
    if norm < 1e-10:
        logger.warning("Near-zero embedding norm %.6f — returning zero vector.", norm)
        return np.zeros_like(embedding)
    return embedding / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute the cosine similarity between two L2-normalized embeddings.

    Parameters
    ----------
    a, b : (512,) unit-normalized float32 vectors.

    Returns
    -------
    Similarity score in [-1, 1]. Higher = more similar.
    """
    a = a.flatten().astype(np.float32)
    b = b.flatten().astype(np.float32)
    return float(np.dot(a, b))


def batch_cosine_similarity(
    query: np.ndarray,
    gallery: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between one query embedding and a gallery matrix.

    Parameters
    ----------
    query   : (512,) unit-normalized float32 vector.
    gallery : (M, 512) unit-normalized float32 matrix.

    Returns
    -------
    (M,) float32 similarity scores.
    """
    query = query.flatten().astype(np.float32)
    gallery = gallery.astype(np.float32)
    return gallery @ query
