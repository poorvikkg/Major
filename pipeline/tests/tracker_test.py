"""
tests/tracker_test.py
---------------------
Unit tests for FaceTracker (ByteTrack implementation).
"""

import unittest

import numpy as np

from pipeline.services.tracker  import FaceTracker, TrackState, _iou, _KalmanBoxTracker
from pipeline.services.detector import DetectionResult


def _make_det(x1=10, y1=10, x2=100, y2=100, score=0.9):
    return DetectionResult(
        box=np.array([x1, y1, x2, y2], dtype=np.float32),
        score=score,
        landmarks=np.zeros((5, 2), dtype=np.float32),
    )


class TestIoU(unittest.TestCase):

    def test_perfect_overlap(self):
        a = np.array([[0, 0, 100, 100]], dtype=np.float32)
        b = np.array([[0, 0, 100, 100]], dtype=np.float32)
        iou = _iou(a, b)
        self.assertAlmostEqual(float(iou[0, 0]), 1.0, places=4)

    def test_no_overlap(self):
        a = np.array([[0, 0, 50, 50]], dtype=np.float32)
        b = np.array([[60, 60, 110, 110]], dtype=np.float32)
        iou = _iou(a, b)
        self.assertAlmostEqual(float(iou[0, 0]), 0.0, places=4)

    def test_partial_overlap(self):
        a = np.array([[0, 0, 100, 100]], dtype=np.float32)
        b = np.array([[50, 0, 150, 100]], dtype=np.float32)
        iou = _iou(a, b)
        self.assertGreater(float(iou[0, 0]), 0.0)
        self.assertLess(float(iou[0, 0]), 1.0)

    def test_output_shape(self):
        a = np.random.rand(5, 4).astype(np.float32) * 100
        b = np.random.rand(3, 4).astype(np.float32) * 100
        # Fix x2 > x1 and y2 > y1
        a[:, 2] += 50
        a[:, 3] += 50
        b[:, 2] += 50
        b[:, 3] += 50
        iou = _iou(a, b)
        self.assertEqual(iou.shape, (5, 3))


class TestKalmanBoxTracker(unittest.TestCase):

    def test_predict_returns_4d(self):
        box = np.array([10, 10, 100, 100], dtype=np.float32)
        kf  = _KalmanBoxTracker(box)
        pred = kf.predict()
        self.assertEqual(pred.shape, (4,))

    def test_update_then_predict_stays_close(self):
        box = np.array([10.0, 10.0, 100.0, 100.0], dtype=np.float32)
        kf  = _KalmanBoxTracker(box)
        kf.update(box)
        pred = kf.predict()
        # After update with same box, prediction should stay close
        np.testing.assert_allclose(pred, box, atol=5.0)


class TestFaceTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = FaceTracker(
            max_age=5,
            min_hits=1,           # report after first hit for test brevity
            iou_threshold=0.3,
            high_conf_thresh=0.5,
        )

    def test_new_detection_spawns_track(self):
        dets = [_make_det(score=0.9)]
        tracks = self.tracker.update(dets)
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].track_id, 1)

    def test_consistent_detection_keeps_same_id(self):
        det = _make_det(score=0.9)
        first = self.tracker.update([det])
        second = self.tracker.update([det])
        self.assertEqual(first[0].track_id, second[0].track_id)

    def test_multiple_people(self):
        det1 = _make_det(10,  10,  100, 100, 0.9)
        det2 = _make_det(300, 300, 400, 400, 0.9)
        tracks = self.tracker.update([det1, det2])
        self.assertEqual(len(tracks), 2)
        ids = {t.track_id for t in tracks}
        self.assertEqual(len(ids), 2)

    def test_track_lost_after_max_age(self):
        det = _make_det(score=0.9)
        self.tracker.update([det])     # spawn
        for _ in range(6):            # age out (max_age=5)
            self.tracker.update([])
        tracks = self.tracker.update([])
        self.assertEqual(len(tracks), 0)

    def test_reset_clears_all_state(self):
        self.tracker.update([_make_det(score=0.9)])
        self.tracker.reset()
        self.assertEqual(len(self.tracker.active_track_ids), 0)
        self.assertEqual(self.tracker.frame_count, 0)

    def test_no_duplicate_ids(self):
        det1 = _make_det(10, 10, 50, 50, 0.9)
        det2 = _make_det(10, 10, 50, 50, 0.9)
        t1 = self.tracker.update([det1])
        t2 = self.tracker.update([det2])
        # Both frames should reference the same track
        self.assertEqual(t1[0].track_id, t2[0].track_id)

    def test_low_confidence_not_spawned(self):
        """Detections below low_conf_thresh should NOT spawn new tracks."""
        det = _make_det(score=0.05)   # below default low_conf_thresh=0.1
        tracks = self.tracker.update([det])
        self.assertEqual(len(tracks), 0)


if __name__ == "__main__":
    unittest.main()
