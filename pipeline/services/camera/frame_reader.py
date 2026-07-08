"""
frame_reader.py
---------------
Purpose  : Read frames from RTSP stream into a FrameBuffer on a dedicated thread.
Inputs   : StreamConfig, FrameBuffer, Event (stop signal), status callback.
Outputs  : Frames pushed to the buffer.
Raises   : N/A (runs infinitely until stopped).

Single Responsibility: Handle cv2.VideoCapture loop and exponential back-off
reconnection logic.
"""

import logging
import threading
import time
from typing import Callable, Optional

import cv2

from pipeline.services.camera.models import StreamConfig, StreamState
from pipeline.services.camera.frame_buffer import FrameBuffer

logger = logging.getLogger(__name__)


class FrameReaderThread(threading.Thread):
    """
    Dedicated thread to continuously read frames from an RTSP stream.
    Handles stream drops and exponential back-off reconnection.
    """

    def __init__(
        self,
        config: StreamConfig,
        frame_buffer: FrameBuffer,
        stop_event: threading.Event,
        on_state_change: Callable[[StreamState], None],
        on_status_emit: Callable[[str], None],
        on_frame_read: Callable[[float], None],
    ):
        super().__init__(name=f"cam_{config.camera_id}_reader", daemon=True)
        self._config = config
        self._buffer = frame_buffer
        self._stop_event = stop_event
        self._on_state_change = on_state_change
        self._on_status_emit = on_status_emit
        self._on_frame_read = on_frame_read
        self._frames_read = 0

    def run(self) -> None:
        reconnect_count = 0
        min_frame_gap = 1.0 / max(self._config.fps_cap, 1)

        while not self._stop_event.is_set():
            cap = self._open_capture()
            if cap is None:
                reconnect_count += 1
                if (
                    self._config.max_reconnect_tries > 0
                    and reconnect_count > self._config.max_reconnect_tries
                ):
                    logger.error(
                        "Camera %d: max reconnect attempts reached — giving up.",
                        self._config.camera_id,
                    )
                    self._stop_event.set()
                    break
                delay = min(self._config.reconnect_delay * reconnect_count, 60)
                logger.warning(
                    "Camera %d reconnect #%d in %.1fs …",
                    self._config.camera_id, reconnect_count, delay,
                )
                self._on_state_change(StreamState.RECONNECTING)
                self._on_status_emit("reconnecting")
                self._stop_event.wait(timeout=delay)
                continue

            reconnect_count = 0
            self._on_state_change(StreamState.RUNNING)
            self._on_status_emit("online")
            logger.info("Camera %d stream opened.", self._config.camera_id)

            last_read = 0.0
            while not self._stop_event.is_set():
                now = time.monotonic()
                elapsed = now - last_read
                if elapsed < min_frame_gap:
                    time.sleep(min_frame_gap - elapsed)

                ret, frame = cap.read()
                last_read = time.monotonic()

                if not ret:
                    logger.warning("Camera %d: lost stream.", self._config.camera_id)
                    break

                self._frames_read += 1
                self._on_frame_read(time.time())
                self._buffer.put_latest(self._frames_read, frame)

            cap.release()
            if not self._stop_event.is_set():
                self._on_state_change(StreamState.RECONNECTING)
                self._on_status_emit("reconnecting")

    def _open_capture(self) -> Optional[cv2.VideoCapture]:
        try:
            cap = cv2.VideoCapture(self._config.stream_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if self._config.capture_width > 0:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.capture_width)
            if self._config.capture_height > 0:
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.capture_height)

            if not cap.isOpened():
                cap.release()
                return None
            return cap
        except Exception:
            logger.exception("Failed to open capture for camera %d.", self._config.camera_id)
            return None

    @property
    def frames_read(self) -> int:
        return self._frames_read
