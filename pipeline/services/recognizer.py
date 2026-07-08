"""
pipeline/services/recognizer.py
-------------------------------
Backward-compatibility shim.

The recognition implementation has been refactored into:
    pipeline/services/recognition/

This file re-exports FaceRecognizer so that existing imports
continue to work without modification. Note that batching logic
has been moved to EmbeddingExtractor.
"""

from pipeline.services.recognition.recognizer import FaceRecognizer

__all__ = [
    "FaceRecognizer",
]
