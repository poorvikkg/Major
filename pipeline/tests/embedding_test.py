"""
embedding_test.py
-----------------
Unit tests for the EmbeddingManager.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from pipeline.services.embedding.embedding_manager import EmbeddingManager


class MockDetector:
    def detect(self, img):
        pass


class MockExtractor:
    def extract(self, img, landmarks):
        return np.random.rand(512).astype(np.float32)


class TestEmbeddingManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = EmbeddingManager(
            detector=MockDetector(),
            extractor=MockExtractor(),
            embeddings_dir=Path(self.temp_dir.name)
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_store_initialization(self):
        self.assertEqual(self.manager.get_store_size(), 0)
        self.assertEqual(len(self.manager.get_metadata()), 0)

    # Note: Full integration testing of register_person requires valid image files,
    # which is better suited for an integration test or mock patching `embed_from_path`.
    
    def test_delete_person_not_found(self):
        self.assertFalse(self.manager.delete_person(999))


if __name__ == "__main__":
    unittest.main()
