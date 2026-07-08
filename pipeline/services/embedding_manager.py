"""
pipeline/services/embedding_manager.py
--------------------------------------
Backward-compatibility shim.

The embedding implementation has been refactored into:
    pipeline/services/embedding/

This file re-exports EmbeddingManager so that existing imports
continue to work without modification.
"""

from pipeline.services.embedding.embedding_manager import EmbeddingManager

__all__ = [
    "EmbeddingManager",
]
