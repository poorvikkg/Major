"""
pipeline/services/embedding/__init__.py
Public API for the embedding sub-package.
"""

from pipeline.services.embedding.embedding_manager import EmbeddingManager
from pipeline.services.embedding.face_image_processor import embed_from_path

__all__ = [
    "EmbeddingManager",
    "embed_from_path",
]
