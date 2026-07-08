"""
tests/recognizer_test.py
------------------------
Unit tests for FaceRecognizer and postprocessing embedding utilities.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from pipeline.services.postprocessing import (
    normalize_embedding,
    cosine_similarity,
    batch_cosine_similarity,
)


class TestEmbeddingUtils(unittest.TestCase):

    def test_normalize_embedding_unit_norm(self):
        raw = np.random.randn(512).astype(np.float32)
        normed = normalize_embedding(raw)
        self.assertAlmostEqual(float(np.linalg.norm(normed)), 1.0, places=5)

    def test_normalize_embedding_shape(self):
        raw = np.random.randn(1, 512).astype(np.float32)
        normed = normalize_embedding(raw)
        self.assertEqual(normed.shape, (512,))

    def test_normalize_zero_vector(self):
        zero = np.zeros(512, dtype=np.float32)
        normed = normalize_embedding(zero)
        self.assertTrue(np.all(normed == 0))

    def test_cosine_similarity_identical(self):
        v = normalize_embedding(np.random.randn(512).astype(np.float32))
        self.assertAlmostEqual(cosine_similarity(v, v), 1.0, places=5)

    def test_cosine_similarity_orthogonal(self):
        a = np.zeros(512, dtype=np.float32)
        b = np.zeros(512, dtype=np.float32)
        a[0] = 1.0
        b[1] = 1.0
        self.assertAlmostEqual(cosine_similarity(a, b), 0.0, places=5)

    def test_cosine_similarity_opposite(self):
        v = normalize_embedding(np.ones(512, dtype=np.float32))
        self.assertAlmostEqual(cosine_similarity(v, -v), -1.0, places=4)

    def test_batch_cosine_similarity_shape(self):
        query   = normalize_embedding(np.random.randn(512).astype(np.float32))
        gallery = np.random.randn(10, 512).astype(np.float32)
        # Normalize gallery rows
        norms   = np.linalg.norm(gallery, axis=1, keepdims=True)
        gallery = gallery / np.maximum(norms, 1e-10)
        scores  = batch_cosine_similarity(query, gallery)
        self.assertEqual(scores.shape, (10,))

    def test_batch_cosine_similarity_range(self):
        query   = normalize_embedding(np.random.randn(512).astype(np.float32))
        gallery = np.vstack([normalize_embedding(np.random.randn(512).astype(np.float32))
                             for _ in range(5)])
        scores  = batch_cosine_similarity(query, gallery)
        self.assertTrue(np.all(scores >= -1.01))
        self.assertTrue(np.all(scores <= 1.01))


class TestFaceRecognizerMocked(unittest.TestCase):

    def _make_mock_session(self, embedding_dim=512):
        session = MagicMock()
        session.get_inputs.return_value = [
            MagicMock(name="input", shape=[1, 3, 112, 112])
        ]
        session.get_outputs.return_value = [
            MagicMock(name="output", shape=[1, embedding_dim])
        ]
        session.get_providers.return_value = ["CPUExecutionProvider"]

        def fake_run(output_names, inputs):
            batch_size = list(inputs.values())[0].shape[0]
            emb = np.random.randn(batch_size, embedding_dim).astype(np.float32)
            return [emb]
        session.run.side_effect = fake_run
        return session

    def test_get_embedding_returns_512d(self):
        from pipeline.services.recognizer import FaceRecognizer
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            rec = FaceRecognizer(
                model_path="models/face_recognition/arcface_r100_finetuned.onnx",
                session=sess,
            )
        crop = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        emb  = rec.get_embedding(crop)
        self.assertIsNotNone(emb)
        self.assertEqual(emb.shape, (512,))

    def test_get_embedding_is_l2_normalized(self):
        from pipeline.services.recognizer import FaceRecognizer
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            rec = FaceRecognizer(
                model_path="models/face_recognition/arcface_r100_finetuned.onnx",
                session=sess,
            )
        crop = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        emb  = rec.get_embedding(crop)
        self.assertAlmostEqual(float(np.linalg.norm(emb)), 1.0, places=4)

    def test_get_embedding_invalid_crop_returns_none(self):
        from pipeline.services.recognizer import FaceRecognizer
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            rec = FaceRecognizer(
                model_path="models/face_recognition/arcface_r100_finetuned.onnx",
                session=sess,
            )
        self.assertIsNone(rec.get_embedding(None))

    def test_get_embeddings_batch_shape(self):
        from pipeline.services.recognizer import FaceRecognizer
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            rec = FaceRecognizer(
                model_path="models/face_recognition/arcface_r100_finetuned.onnx",
                session=sess,
            )
        crops = [np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8) for _ in range(5)]
        embs  = rec.get_embeddings_batch(crops)
        self.assertEqual(embs.shape, (5, 512))

    def test_get_embeddings_batch_empty_returns_empty(self):
        from pipeline.services.recognizer import FaceRecognizer
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            rec = FaceRecognizer(
                model_path="models/face_recognition/arcface_r100_finetuned.onnx",
                session=sess,
            )
        embs = rec.get_embeddings_batch([])
        self.assertEqual(embs.shape[0], 0)


if __name__ == "__main__":
    unittest.main()
