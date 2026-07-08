"""
stream_processor.py
-------------------
Purpose  : Facade for an RTSP camera stream processor.
Inputs   : Dependencies (Inference, Tracker, Notifier, DB) and config.
Outputs  : Spawns reader and processor threads.
Raises   : N/A

Single Responsibility: Provide a unified interface to start/stop the two-thread
stream processing pipeline.
"""

import logging
import threading
from typing import Dict, Optional

from pipeline.services.camera.models import StreamConfig, StreamState
from pipeline.services.camera.frame_buffer import FrameBuffer
from pipeline.services.camera.frame_reader import FrameReaderThread
from pipeline.services.camera.processor_thread import ProcessorThread
from pipeline.services.inference import FaceInference
from pipeline.services.tracking.tracker import FaceTracker
from pipeline.services.notifier import Notifier
from pipeline.services.api import BackendSocketClient
from pipeline.database.postgres import PostgresRepository

logger = logging.getLogger(__name__)


class StreamProcessor:
    """
    Manages one RTSP camera stream end-to-end.
    """

    def __init__(
        self,
        config:        StreamConfig,
        inference:     FaceInference,
        notifier:      Notifier,
        db_repo:       PostgresRepository,
        tracker:       FaceTracker,
        socket_client: Optional[BackendSocketClient] = None,
    ) -> None:
        self._config = config
        self._inference = inference
        self._notifier = notifier
        self._db = db_repo
        self._tracker = tracker
        self._socket = socket_client

        self._state = StreamState.IDLE
        self._state_lock = threading.Lock()
        self._stop_event = threading.Event()

        self._frame_buffer = FrameBuffer(maxsize=config.frame_buffer_size)

        self._reader_thread: Optional[FrameReaderThread] = None
        self._processor_thread: Optional[ProcessorThread] = None

        self._last_frame_ts = 0.0
        self._name_cache: Dict[int, str] = {}

        logger.info(
            "StreamProcessor created | camera_id=%d | url=%s | skip=%d",
            config.camera_id, config.stream_url, config.frame_skip,
        )

    def start(self) -> None:
        with self._state_lock:
            if self._state not in (StreamState.IDLE, StreamState.STOPPED):
                logger.warning(
                    "StreamProcessor (cam=%d) already running — ignoring start().",
                    self._config.camera_id,
                )
                return
            self._stop_event.clear()
            self._state = StreamState.CONNECTING

        self._reader_thread = FrameReaderThread(
            config=self._config,
            frame_buffer=self._frame_buffer,
            stop_event=self._stop_event,
            on_state_change=self._set_state,
            on_status_emit=self._emit_status,
            on_frame_read=self._on_frame_read,
        )
        self._processor_thread = ProcessorThread(
            config=self._config,
            frame_buffer=self._frame_buffer,
            stop_event=self._stop_event,
            inference=self._inference,
            tracker=self._tracker,
            notifier=self._notifier,
            name_resolver=self._resolve_name,
            on_frame_processed=lambda: None,
        )

        self._reader_thread.start()
        self._processor_thread.start()
        logger.info("StreamProcessor started | camera_id=%d.", self._config.camera_id)

    def stop(self) -> None:
        logger.info("Stopping StreamProcessor | camera_id=%d.", self._config.camera_id)
        self._stop_event.set()

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=10)

        if self._processor_thread and self._processor_thread.is_alive():
            self._processor_thread.join(timeout=10)

        with self._state_lock:
            self._state = StreamState.STOPPED

        self._tracker.reset()
        self._notifier.reset_all_cooldowns()
        self._emit_status("offline")
        logger.info("StreamProcessor stopped | camera_id=%d.", self._config.camera_id)

    @property
    def is_running(self) -> bool:
        return self._state == StreamState.RUNNING

    @property
    def camera_id(self) -> int:
        return self._config.camera_id

    def get_metrics(self) -> Dict:
        return {
            "camera_id":       self._config.camera_id,
            "state":           self._state.name,
            "frames_read":     self._reader_thread.frames_read if self._reader_thread else 0,
            "frames_processed": self._processor_thread.frames_processed if self._processor_thread else 0,
            "total_matches":   self._processor_thread.total_matches if self._processor_thread else 0,
            "last_frame_ts":   self._last_frame_ts,
        }

    # ------------------------------------------------------------------
    # Callbacks & Helpers
    # ------------------------------------------------------------------

    def _set_state(self, state: StreamState) -> None:
        with self._state_lock:
            self._state = state

    def _emit_status(self, status: str) -> None:
        if self._socket:
            try:
                self._socket.emit_camera_status(self._config.camera_id, status)
            except Exception:
                pass

    def _on_frame_read(self, ts: float) -> None:
        self._last_frame_ts = ts

    def _resolve_name(self, person_id: int) -> str:
        if person_id not in self._name_cache:
            try:
                person = self._db.get_missing_person_by_id(person_id)
                self._name_cache[person_id] = person["name"] if person else "Unknown"
            except Exception:
                self._name_cache[person_id] = "Unknown"
        return self._name_cache[person_id]
