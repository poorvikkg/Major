"""
detector.py
-----------
Purpose  : FaceDetector inference class.
Inputs   : BGR frames, ONNX model path, thresholds.
Outputs  : List[DetectionResult].
Raises   : FileNotFoundError on missing ONNX model.

Single Responsibility: Manage the ONNX session and detect faces.
Image processing, NMS, and results generation is delegated.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
import onnxruntime as ort

from pipeline.services.preprocessing import normalize_for_detector, align_face
from pipeline.services.postprocessing import decode_scrfd_outputs, clip_boxes
from pipeline.services.detection.detection_result import DetectionResult

logger = logging.getLogger(__name__)


class FaceDetector:
    """
    SCRFD-10G face detector wrapping an ONNX Runtime inference session.
    """

    _INPUT_SIZE: Tuple[int, int] = (640, 640)   # (width, height)

    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.5,
        nms_threshold: float  = 0.4,
        session: Optional[ort.InferenceSession] = None,
    ) -> None:
        self.model_path      = Path(model_path)
        self.conf_threshold  = conf_threshold
        self.nms_threshold   = nms_threshold
        self._session        = session
        self._input_name: Optional[str] = None

        if self._session is None:
            self._session = self._build_session()
        self._input_name = self._session.get_inputs()[0].name
        logger.info(
            "FaceDetector ready | model=%s | conf=%.2f | nms=%.2f | providers=%s",
            self.model_path.name,
            self.conf_threshold,
            self.nms_threshold,
            self._session.get_providers(),
        )

    def detect_faces(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect all faces in a BGR frame."""
        if frame is None or frame.size == 0:
            logger.warning("detect_faces received empty frame — returning [].")
            return []

        try:
            blob, scale, offset = normalize_for_detector(frame, self._INPUT_SIZE)
            raw_outputs = self._run_inference(blob)
            boxes, scores, landmarks = decode_scrfd_outputs(
                raw_outputs,
                input_size=self._INPUT_SIZE,
                conf_threshold=self.conf_threshold,
                nms_threshold=self.nms_threshold,
                scale=scale,
                offset=offset,
            )
            boxes = clip_boxes(boxes, frame.shape[:2])
            results = [
                DetectionResult(
                    box=boxes[i],
                    score=float(scores[i]),
                    landmarks=landmarks[i],
                )
                for i in range(len(scores))
            ]
            results.sort(key=lambda r: r.score, reverse=True)
            logger.debug("Detected %d face(s).", len(results))
            return results

        except Exception:
            logger.exception("Error in detect_faces — returning [].")
            return []

    def detect_landmarks(self, frame: np.ndarray) -> List[np.ndarray]:
        """Returns only the 5-point landmarks for each detected face."""
        results = self.detect_faces(frame)
        return [r.landmarks for r in results]

    def draw_boxes(
        self,
        frame: np.ndarray,
        results: List[DetectionResult],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
        draw_landmarks: bool = True,
        draw_score: bool = True,
    ) -> np.ndarray:
        """Draw bounding boxes and landmarks on a copy of the frame."""
        canvas = frame.copy()
        landmark_colors = [
            (0, 0, 255),    # left eye
            (0, 255, 255),  # right eye
            (0, 128, 255),  # nose
            (255, 0, 255),  # mouth left
            (255, 128, 0),  # mouth right
        ]

        for result in results:
            x1, y1, x2, y2 = result.xyxy
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, thickness)

            if draw_score:
                label = f"{result.score:.2f}"
                cv2.putText(
                    canvas, label, (x1, max(y1 - 8, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, thickness
                )

            if draw_landmarks:
                for pt_idx, pt in enumerate(result.landmarks):
                    cx, cy = int(pt[0]), int(pt[1])
                    lc = landmark_colors[pt_idx % len(landmark_colors)]
                    cv2.circle(canvas, (cx, cy), 3, lc, -1)

        return canvas

    def get_aligned_crops(
        self,
        frame: np.ndarray,
        results: Optional[List[DetectionResult]] = None,
    ) -> List[np.ndarray]:
        """Return 112 x 112 aligned face crops for every detected face."""
        if results is None:
            results = self.detect_faces(frame)

        crops: List[np.ndarray] = []
        for result in results:
            crop = align_face(frame, result.landmarks)
            if crop is not None:
                crops.append(crop)
            else:
                logger.warning("Alignment failed for a face — skipping crop.")
        return crops

    def _build_session(self) -> ort.InferenceSession:
        if not self.model_path.exists():
            raise FileNotFoundError(f"SCRFD model not found at: {self.model_path}")

        providers = self._resolve_providers()
        logger.info("Loading SCRFD model from %s with providers: %s", self.model_path, providers)
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 4

        try:
            session = ort.InferenceSession(
                str(self.model_path),
                sess_options=opts,
                providers=providers,
            )
        except Exception as exc:
            if "CUDAExecutionProvider" in str(providers):
                logger.warning("CUDA provider failed (%s) — falling back to CPU.", exc)
                session = ort.InferenceSession(
                    str(self.model_path),
                    sess_options=opts,
                    providers=["CPUExecutionProvider"],
                )
            else:
                raise

        return session

    @staticmethod
    def _resolve_providers() -> List[str]:
        available = ort.get_available_providers()
        logger.debug("Available ORT providers: %s", available)
        preferred = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        return [p for p in preferred if p in available] or ["CPUExecutionProvider"]

    def _run_inference(self, blob: np.ndarray) -> List[np.ndarray]:
        t0 = time.perf_counter()
        outputs = self._session.run(None, {self._input_name: blob})
        t1 = time.perf_counter()
        logger.debug("SCRFD _run_inference completed in %.1f ms", (t1 - t0) * 1000)
        return outputs
