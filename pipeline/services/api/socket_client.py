"""
socket_client.py
----------------
Purpose  : Socket.IO client for emitting real-time detection events.
"""

import logging
import threading
from typing import Any, Dict

import socketio

from pipeline.services.api.config import SOCKET_URL, API_KEY

logger = logging.getLogger(__name__)


class BackendSocketClient:
    """
    Socket.IO client that emits real-time detection events to the Node.js server.
    Connection is established lazily on first emit and automatically
    re-established if disconnected.
    """

    _RECONNECT_DELAY = 3.0  # seconds between reconnect attempts

    def __init__(
        self,
        socket_url: str = SOCKET_URL,
        api_key:    str = API_KEY,
    ) -> None:
        self._url      = socket_url
        self._api_key  = api_key
        self._sio      = socketio.Client(
            reconnection=True,
            reconnection_attempts=0,        # infinite reconnect
            reconnection_delay=self._RECONNECT_DELAY,
            logger=False,
            engineio_logger=False,
        )
        self._connected   = False
        self._connect_lock = threading.Lock()
        
        self._sio.on("connect",    self._on_connect)
        self._sio.on("disconnect", self._on_disconnect)

        logger.info("BackendSocketClient initialised | url=%s", self._url)

    def emit_detection(self, payload: Dict[str, Any]) -> None:
        thread = threading.Thread(
            target=self._emit_async,
            args=("detection_alert", payload),
            daemon=True,
        )
        thread.start()

    def emit_camera_status(self, camera_id: int, status: str) -> None:
        thread = threading.Thread(
            target=self._emit_async,
            args=("camera_status", {"camera_id": camera_id, "status": status}),
            daemon=True,
        )
        thread.start()

    def emit_video_progress(self, job_id: str, progress: float, status: str) -> None:
        thread = threading.Thread(
            target=self._emit_async,
            args=(
                "video_progress",
                {"job_id": job_id, "progress": round(progress, 1), "status": status},
            ),
            daemon=True,
        )
        thread.start()

    def connect(self) -> bool:
        with self._connect_lock:
            if self._connected:
                return True
            try:
                auth = {"token": self._api_key} if self._api_key else {}
                self._sio.connect(
                    self._url,
                    auth=auth,
                    transports=["websocket", "polling"],
                    wait_timeout=5,
                )
                return True
            except Exception:
                logger.warning("Socket.IO connection failed to %s.", self._url)
                return False

    def disconnect(self) -> None:
        if self._sio.connected:
            self._sio.disconnect()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _emit_async(self, event: str, data: Dict) -> None:
        if not self._connected:
            self.connect()

        if not self._connected:
            logger.warning("Socket.IO not connected — dropping event '%s'.", event)
            return

        try:
            self._sio.emit(event, data)
            logger.debug("Socket.IO emitted '%s' | person_id=%s", event, data.get("person_id"))
        except Exception:
            logger.exception("Socket.IO emit '%s' failed.", event)

    def _on_connect(self) -> None:
        self._connected = True
        logger.info("Socket.IO connected to %s.", self._url)

    def _on_disconnect(self) -> None:
        self._connected = False
        logger.warning("Socket.IO disconnected from %s.", self._url)
