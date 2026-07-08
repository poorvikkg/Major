"""
tests/integration_test.py
--------------------------
Integration tests that wire together multiple pipeline components.

These tests use:
- Mocked ONNX sessions (no real model files needed)
- Temporary directories for embedding / FAISS storage
- Real numpy operations and FAISS index (in-memory via temp dir)

They verify the full registration → search → track → notify data flow
without external dependencies (DB / backend server).
"""

import shutil
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone

import numpy as np

_DIM = 512


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rand_unit(n=1) -> np.ndarray:
    v = np.random.randn(n, _DIM).astype(np.float32)
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return (v / norms).squeeze(0) if n == 1 else v / norms


def _make_mock_detector_session():
    sess = MagicMock()
    sess.get_inputs.return_value  = [MagicMock(name="input")]
    sess.get_outputs.return_value = [MagicMock(name="output")]
    sess.get_providers.return_value = ["CPUExecutionProvider"]
    sess.run.return_value = [np.zeros((1, 1, 1), dtype=np.float32)] * 9
    return sess


def _make_mock_recognizer_session(embedding: np.ndarray):
    """Returns a recognizer session that always outputs the given embedding."""
    sess = MagicMock()
    sess.get_inputs.return_value  = [MagicMock(name="input",  shape=[1, 3, 112, 112])]
    sess.get_outputs.return_value = [MagicMock(name="output", shape=[1, _DIM])]
    sess.get_providers.return_value = ["CPUExecutionProvider"]
    def fake_run(output_names, inputs):
        batch_size = list(inputs.values())[0].shape[0]
        return [np.tile(embedding, (batch_size, 1))]
    sess.run.side_effect = fake_run
    return sess


# ---------------------------------------------------------------------------
# Integration: EmbeddingManager + FAISSManager
# ---------------------------------------------------------------------------

class TestEmbeddingFAISSIntegration(unittest.TestCase):
    """
    Test that registering a person in EmbeddingManager and syncing to
    FAISSManager allows the person to be found via FAISS search.
    """

    def setUp(self):
        self.tmpdir    = tempfile.mkdtemp()
        self.emb_dir   = Path(self.tmpdir) / "embeddings"
        self.faiss_dir = Path(self.tmpdir) / "faiss"
        self.faces_dir = Path(self.tmpdir) / "registered_faces" / "1"
        self.faces_dir.mkdir(parents=True)

        import cv2
        # Create a dummy face image file
        dummy_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        self.img_path = str(self.faces_dir / "img1.jpg")
        cv2.imwrite(self.img_path, dummy_face)

        # Set up known embedding
        self.known_embedding = _rand_unit()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _build_components(self):
        from pipeline.services.detection.detector import FaceDetector
        from pipeline.services.recognition.recognizer import FaceRecognizer
        from pipeline.services.recognition.embedding_extractor import EmbeddingExtractor
        from pipeline.services.embedding.embedding_manager import EmbeddingManager
        from pipeline.services.faiss.faiss_manager import FAISSManager

        det_sess = _make_mock_detector_session()
        rec_sess = _make_mock_recognizer_session(self.known_embedding)

        with patch.object(Path, "exists", return_value=True):
            detector   = FaceDetector("mock.onnx", session=det_sess)
            recognizer = FaceRecognizer("mock.onnx", session=rec_sess)

        # Patch detector.detect_faces to return one fake detection
        from pipeline.services.detection.detection_result import DetectionResult
        fake_det = DetectionResult(
            box=np.array([10, 10, 100, 100], dtype=np.float32),
            score=0.95,
            landmarks=np.array([
                [38, 51], [73, 51], [56, 71], [41, 92], [70, 92]
            ], dtype=np.float32),
        )
        detector.detect_faces = MagicMock(return_value=[fake_det])
        detector.get_aligned_crops = MagicMock(
            return_value=[np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)]
        )

        extractor = EmbeddingExtractor(recognizer)
        emb_mgr  = EmbeddingManager(detector, extractor, embeddings_dir=self.emb_dir)
        faiss_mgr = FAISSManager(faiss_dir=self.faiss_dir)

        return emb_mgr, faiss_mgr, recognizer

    def test_register_then_search_finds_person(self):
        emb_mgr, faiss_mgr, _ = self._build_components()
        from pipeline.services.recognition_service import RecognitionService
        from pipeline.services.inference import FaceInference

        # Register person 1
        emb_mgr.register_person(person_id=1, image_paths=[self.img_path])
        embeddings, user_ids = emb_mgr.get_all_embeddings()

        faiss_mgr.sync_from_store(embeddings, user_ids)

        # Search with the same embedding the recognizer outputs
        results = faiss_mgr.search(self.known_embedding, top_k=1, threshold=0.5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["person_id"], 1)
        self.assertGreater(results[0]["score"], 0.5)

    def test_register_delete_not_found(self):
        emb_mgr, faiss_mgr, _ = self._build_components()

        emb_mgr.register_person(person_id=2, image_paths=[self.img_path])
        embeddings, user_ids = emb_mgr.get_all_embeddings()
        faiss_mgr.sync_from_store(embeddings, user_ids)

        # Delete
        emb_mgr.delete_person(person_id=2)
        faiss_mgr.delete_person(person_id=2)

        results = faiss_mgr.search(self.known_embedding, top_k=1, threshold=0.5)
        person_ids = [r["person_id"] for r in results]
        self.assertNotIn(2, person_ids)

    def test_multiple_persons_correct_match(self):
        emb_mgr, faiss_mgr, _ = self._build_components()

        # Register person 1 with known_embedding
        emb_mgr.register_person(person_id=1, image_paths=[self.img_path])

        # Register person 2 with a completely different embedding
        other_embedding = _rand_unit()
        faiss_mgr.sync_from_store(
            *emb_mgr.get_all_embeddings()
        )
        faiss_mgr.add_person(person_id=2, embedding=other_embedding)

        # Search for person 1's embedding
        results = faiss_mgr.search(self.known_embedding, top_k=2, threshold=0.0)
        top_pid = results[0]["person_id"] if results else None
        # Person 1 should rank higher for their own embedding
        self.assertEqual(top_pid, 1)


# ---------------------------------------------------------------------------
# Integration: FaceTracker + detection pipeline
# ---------------------------------------------------------------------------

class TestTrackerIntegration(unittest.TestCase):

    def test_track_ids_stable_across_frames(self):
        from pipeline.services.tracking.tracker  import FaceTracker
        from pipeline.services.detection.detection_result import DetectionResult

        tracker = FaceTracker(max_age=10, min_hits=1, high_conf_thresh=0.5)
        det = DetectionResult(
            box=np.array([50, 50, 150, 150], dtype=np.float32),
            score=0.92,
            landmarks=np.zeros((5, 2), dtype=np.float32),
        )
        ids_seen = set()
        for _ in range(5):
            tracks = tracker.update([det])
            for t in tracks:
                ids_seen.add(t.track_id)

        # All frames should reference the same track
        self.assertEqual(len(ids_seen), 1)

    def test_two_detections_two_track_ids(self):
        from pipeline.services.tracking.tracker  import FaceTracker
        from pipeline.services.detection.detection_result import DetectionResult

        tracker = FaceTracker(max_age=10, min_hits=1, high_conf_thresh=0.5)
        dets = [
            DetectionResult(
                box=np.array([0,   0,  50,  50], dtype=np.float32),
                score=0.9,
                landmarks=np.zeros((5, 2), dtype=np.float32),
            ),
            DetectionResult(
                box=np.array([300, 300, 400, 400], dtype=np.float32),
                score=0.9,
                landmarks=np.zeros((5, 2), dtype=np.float32),
            ),
        ]
        tracks = tracker.update(dets)
        self.assertEqual(len(tracks), 2)
        self.assertNotEqual(tracks[0].track_id, tracks[1].track_id)


# ---------------------------------------------------------------------------
# Integration: Notifier cooldown
# ---------------------------------------------------------------------------

class TestNotifierCooldown(unittest.TestCase):

    def _make_notifier(self, cooldown=5):
        from pipeline.services.notifier import Notifier
        http   = MagicMock()
        http.post_detection.return_value = True
        socket = MagicMock()
        db     = MagicMock()
        db.insert_detection_log.return_value = 1
        notifier = Notifier(
            http_client=http,
            socket_client=socket,
            db_repo=db,
            cooldown_sec=cooldown,
            save_frames=False,
        )
        return notifier, http, socket, db

    def test_first_notify_dispatches(self):
        notifier, http, socket, db = self._make_notifier(cooldown=30)
        result = notifier.notify(
            person_id=1, person_name="Test", camera_id=1,
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        self.assertTrue(result)
        http.post_detection.assert_called_once()

    def test_second_notify_suppressed(self):
        notifier, http, socket, db = self._make_notifier(cooldown=30)
        notifier.notify(
            person_id=1, person_name="Test", camera_id=1,
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        # Second call immediately — should be suppressed
        result = notifier.notify(
            person_id=1, person_name="Test", camera_id=1,
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        self.assertFalse(result)
        http.post_detection.assert_called_once()  # only once

    def test_different_camera_different_cooldown(self):
        notifier, http, _, _ = self._make_notifier(cooldown=30)
        notifier.notify(
            person_id=1, person_name="Test", camera_id=1,
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        result = notifier.notify(
            person_id=1, person_name="Test", camera_id=2,  # different camera
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        self.assertTrue(result)
        self.assertEqual(http.post_detection.call_count, 2)

    def test_reset_cooldown_allows_retry(self):
        notifier, http, _, _ = self._make_notifier(cooldown=30)
        notifier.notify(
            person_id=1, person_name="Test", camera_id=1,
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        notifier.reset_cooldown(person_id=1, camera_id=1)
        result = notifier.notify(
            person_id=1, person_name="Test", camera_id=1,
            score=0.8, box=np.array([0, 0, 100, 100], dtype=np.float32),
        )
        self.assertTrue(result)
        self.assertEqual(http.post_detection.call_count, 2)


if __name__ == "__main__":
    unittest.main()
