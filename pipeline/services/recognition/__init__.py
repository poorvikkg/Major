"""
pipeline/services/recognition/__init__.py
Public API for the recognition sub-package.
"""

from pipeline.services.recognition.recognizer import FaceRecognizer
from pipeline.services.recognition.embedding_extractor import EmbeddingExtractor
from pipeline.services.recognition.similarity import (
    normalize_embedding,
    cosine_similarity,
    batch_cosine_similarity,
)

__all__ = [
    "FaceRecognizer",
    "EmbeddingExtractor",
    "normalize_embedding",
    "cosine_similarity",
    "batch_cosine_similarity",
]
