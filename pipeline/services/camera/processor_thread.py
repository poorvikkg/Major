"""
processor_thread.py
-------------------
Purpose  : Consume frames from the buffer, run inference, tracking, and notifications.
Inputs   : FrameBuffer, FaceInference, FaceTracker, Notifier.
Outputs  : Notifications emitted for recognized faces.
Raises   : N/A (runs infinitely until stopped).

Single Responsibility: Coordinate AI processing and alerting for a single camera.
"""

import logging
import queue
import threading
from typing import Callable, Optional

import numpy as np

from pipeline.services.camera.models import StreamConfig
from pipeline.services.camera.frame_buffer import FrameBuffer
from pipeline.services.inference import FaceInference
from pipeline.services.tracking.tracker import FaceTracker
from pipeline.services.notifier import Notifier
from pipeline.services.detection.detection_result import DetectionResult

logger = logging.getLogger(__name__)


class ProcessorThread(threading.Thread):
    """
    Dedicated thread to run heavy inference logic on frames.
    Avoids blocking the RTSP reader thread.
    """

    def __init__(
        self,
        config: StreamConfig,
        frame_buffer: FrameBuffer,
        stop_event: threading.Event,
        inference: FaceInference,
        tracker: FaceTracker,
        notifier: Notifier,
        name_resolver: Callable[[int], str],
        on_frame_processed: Callable[[], None],
    ):
        super().__init__(name=f"cam_{config.camera_id}_processor", daemon=True)
        self._config = config
        self._buffer = frame_buffer
        self._stop_event = stop_event
        self._inference = inference
        self._tracker = tracker
        self._notifier = notifier
        self._name_resolver = name_resolver
        self._on_frame_processed = on_frame_processed

        self._frames_processed = 0
        self._total_matches = 0

    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                frame_idx, frame = self._buffer.get(timeout=1.0)
            except queue.Empty:
                continue

            # Frame skip: only process every N-th frame
            if frame_idx % max(self._config.frame_skip, 1) != 0:
                continue

            self._frames_processed += 1
            self._on_frame_processed()

            try:
                self._process_frame(frame)
            except Exception:
                logger.exception(
                    "Error processing frame %d on camera %d.",
                    frame_idx, self._config.camera_id,
                )

    def _process_frame(self, frame: np.ndarray) -> None:
        """Run inference + tracking on one frame and notify on matches."""
        # 1. Run detection + recognition
        results = self._inference.run(frame)
        if not results:
            return

        # 2. Update tracker with raw detection results
        det_objects = [
            DetectionResult(box=r.box, score=r.score, landmarks=r.landmarks)
            for r in results
        ]
        active_tracks = self._tracker.update(det_objects)
        track_id_map  = {id(dt): t.track_id for dt, t in zip(det_objects, active_tracks)}

        # 3. Dispatch notifications for confirmed matches
        for result in results:
            if not result.is_match or result.person_id is None:
                continue

            # Only notify if this face corresponds to a confirmed track
            track_id = track_id_map.get(id(result), None)

            name = self._name_resolver(result.person_id)
            self._notifier.notify(
                person_id   = result.person_id,
                person_name = name,
                camera_id   = self._config.camera_id,
                score       = result.score,
                box         = result.box,
                track_id    = track_id,
                frame       = frame,
            )
            self._total_matches += 1

    @property
    def frames_processed(self) -> int:
        return self._frames_processed

    @property
    def total_matches(self) -> int:
        return self._total_matches
