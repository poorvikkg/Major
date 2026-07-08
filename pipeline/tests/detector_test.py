"""
tests/detector_test.py
----------------------
Unit tests for FaceDetector and preprocessing utilities.

All tests use mocked ONNX sessions to avoid needing the actual model file.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from pipeline.services.preprocessing import (
    normalize_for_detector,
    normalize_for_recognizer,
    align_face,
    _letterbox,
    _ensure_bgr_uint8,
)
from pipeline.services.postprocessing import clip_boxes


class TestPreprocessing(unittest.TestCase):

    def _make_frame(self, h=480, w=640):
        return np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)

    # ------------------------------------------------------------------
    # normalize_for_detector
    # ------------------------------------------------------------------

    def test_detector_blob_shape(self):
        frame = self._make_frame()
        blob, scale, offset = normalize_for_detector(frame, target_size=(640, 640))
        self.assertEqual(blob.shape, (1, 3, 640, 640))
        self.assertEqual(blob.dtype, np.float32)

    def test_detector_scale_is_positive(self):
        frame = self._make_frame(720, 1280)
        _, scale, _ = normalize_for_detector(frame, (640, 640))
        self.assertGreater(scale, 0)
        self.assertLessEqual(scale, 1.0)

    def test_detector_blob_range(self):
        """Normalized values should be roughly in [-1, 1]."""
        frame = self._make_frame()
        blob, _, _ = normalize_for_detector(frame, (640, 640))
        self.assertLessEqual(float(blob.max()), 1.5)
        self.assertGreaterEqual(float(blob.min()), -1.5)

    # ------------------------------------------------------------------
    # normalize_for_recognizer
    # ------------------------------------------------------------------

    def test_recognizer_blob_shape(self):
        crop = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        blob = normalize_for_recognizer(crop)
        self.assertEqual(blob.shape, (1, 3, 112, 112))
        self.assertEqual(blob.dtype, np.float32)

    def test_recognizer_blob_range(self):
        """Values should be in [-1, 1]."""
        crop = np.full((112, 112, 3), 127, dtype=np.uint8)
        blob = normalize_for_recognizer(crop)
        self.assertAlmostEqual(float(blob.max()), 0.0, places=1)

    def test_recognizer_resizes_non_112(self):
        """Input that is not 112x112 should be auto-resized."""
        crop = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        blob = normalize_for_recognizer(crop)
        self.assertEqual(blob.shape, (1, 3, 112, 112))

    # ------------------------------------------------------------------
    # align_face
    # ------------------------------------------------------------------

    def test_align_face_valid_landmarks(self):
        frame = self._make_frame()
        lm = np.array([
            [100, 150], [200, 150], [150, 200], [110, 250], [190, 250]
        ], dtype=np.float32)
        crop = align_face(frame, lm)
        self.assertIsNotNone(crop)
        self.assertEqual(crop.shape, (112, 112, 3))

    def test_align_face_invalid_shape(self):
        frame = self._make_frame()
        bad_lm = np.zeros((4, 2), dtype=np.float32)  # wrong: needs 5 pts
        crop = align_face(frame, bad_lm)
        self.assertIsNone(crop)

    # ------------------------------------------------------------------
    # _ensure_bgr_uint8
    # ------------------------------------------------------------------

    def test_grayscale_to_bgr(self):
        gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        bgr = _ensure_bgr_uint8(gray)
        self.assertEqual(bgr.shape[2], 3)

    def test_float_image_coercion(self):
        img_float = np.random.rand(100, 100, 3).astype(np.float32)
        result = _ensure_bgr_uint8(img_float)
        self.assertEqual(result.dtype, np.uint8)

    def test_empty_image_raises(self):
        with self.assertRaises(ValueError):
            _ensure_bgr_uint8(np.array([]))

    # ------------------------------------------------------------------
    # clip_boxes
    # ------------------------------------------------------------------

    def test_clip_boxes_within_bounds(self):
        boxes = np.array([[-10, -10, 700, 500]], dtype=np.float32)
        clipped = clip_boxes(boxes, image_shape=(480, 640))
        self.assertGreaterEqual(float(clipped[0, 0]), 0)
        self.assertLessEqual(float(clipped[0, 2]), 640)

    def test_clip_boxes_no_change_when_in_bounds(self):
        boxes = np.array([[10, 10, 200, 200]], dtype=np.float32)
        clipped = clip_boxes(boxes, image_shape=(480, 640))
        np.testing.assert_array_equal(boxes, clipped)


class TestFaceDetectorMocked(unittest.TestCase):
    """FaceDetector tests with a mocked ONNX session."""

    def _make_mock_session(self):
        session = MagicMock()
        session.get_inputs.return_value  = [MagicMock(name="input")]
        session.get_outputs.return_value = [MagicMock(name="output")]
        session.get_providers.return_value = ["CPUExecutionProvider"]
        # Return 9 zero tensors as SCRFD output
        def fake_run(outputs, inputs):
            batch = list(inputs.values())[0]
            return [np.zeros((1, 1, 1), dtype=np.float32) for _ in range(9)]
        session.run.side_effect = fake_run
        return session

    def test_detect_faces_empty_frame_returns_empty(self):
        from pipeline.services.detector import FaceDetector
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            det = FaceDetector(
                model_path="models/face_detection/scrfd_10g_bnkps.onnx",
                session=sess,
            )
        result = det.detect_faces(np.array([]))
        self.assertEqual(result, [])

    def test_detect_faces_valid_frame_returns_list(self):
        from pipeline.services.detector import FaceDetector
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            det = FaceDetector(
                model_path="models/face_detection/scrfd_10g_bnkps.onnx",
                session=sess,
            )
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = det.detect_faces(frame)
        self.assertIsInstance(result, list)

    def test_draw_boxes_returns_frame_copy(self):
        from pipeline.services.detector import FaceDetector, DetectionResult
        sess = self._make_mock_session()
        with patch.object(Path, "exists", return_value=True):
            det = FaceDetector(
                model_path="models/face_detection/scrfd_10g_bnkps.onnx",
                session=sess,
            )
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = [
            DetectionResult(
                box=np.array([10, 10, 100, 100], dtype=np.float32),
                score=0.9,
                landmarks=np.zeros((5, 2), dtype=np.float32),
            )
        ]
        annotated = det.draw_boxes(frame, results)
        self.assertEqual(annotated.shape, frame.shape)
        # Original must not be mutated
        self.assertTrue(np.all(frame == 0))


if __name__ == "__main__":
    unittest.main()
