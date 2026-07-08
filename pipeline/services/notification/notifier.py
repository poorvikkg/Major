"""
notifier.py
-----------
Detection notification service.
"""

import logging
import threading
import time
from typing import Dict, Optional, Tuple

import numpy as np

from pipeline.services.api.http_client import BackendHTTPClient
from pipeline.services.api.socket_client import BackendSocketClient
from pipeline.services.utils import build_detection_payload, save_frame, utc_now
from pipeline.database.postgres import PostgresRepository
from pipeline.config import get_config

logger = logging.getLogger(__name__)

_DEFAULT_COOLDOWN_SECONDS = 30


class Notifier:
    """
    Stateful detection notification dispatcher.
    """

    def __init__(
        self,
        http_client:        BackendHTTPClient,
        socket_client:      BackendSocketClient,
        db_repo:            PostgresRepository,
        cooldown_sec:       int  = _DEFAULT_COOLDOWN_SECONDS,
        save_frames:        bool = True,
        include_frame_b64:  bool = False,
    ) -> None:
        self._http          = http_client
        self._socket        = socket_client
        self._db            = db_repo
        self._cooldown      = cooldown_sec
        self._save_frames   = save_frames
        self._include_b64   = include_frame_b64

        self._cooldown_map:  Dict[Tuple[int, int], float] = {}
        self._cooldown_lock: threading.Lock               = threading.Lock()

        logger.info(
            "Notifier initialised | cooldown=%ds | save_frames=%s",
            cooldown_sec, save_frames,
        )

    def notify(
        self,
        person_id:   int,
        person_name: str,
        camera_id:   int,
        score:       float,
        box:         np.ndarray,
        track_id:    Optional[int] = None,
        frame:       Optional[np.ndarray] = None,
    ) -> bool:
        if not self._cooldown_check(person_id, camera_id):
            logger.debug(
                "Notification suppressed (cooldown) | person_id=%d | camera_id=%d",
                person_id, camera_id,
            )
            return False

        frame_path: Optional[str] = None
        if self._save_frames and frame is not None:
            frame_path = save_frame(
                frame=frame,
                directory=get_config().paths.uploads_images_dir,
                filename=f"det_{person_id}_{camera_id}_{int(time.time())}",
            )

        payload = build_detection_payload(
            person_id=person_id,
            person_name=person_name,
            camera_id=camera_id,
            score=score,
            box=box,
            track_id=track_id,
            frame=frame if self._include_b64 else None,
            frame_path=frame_path,
            include_frame=self._include_b64,
        )

        try:
            self._http.post_detection(payload)
        except Exception:
            logger.exception("HTTP notification failed for person_id=%d.", person_id)

        try:
            self._socket.emit_detection(payload)
        except Exception:
            logger.exception("Socket.IO notification failed for person_id=%d.", person_id)

        try:
            from pipeline.services.utils import xyxy_to_dict
            self._db.insert_detection_log(
                person_id=person_id,
                camera_id=camera_id,
                similarity_score=score,
                bounding_box=xyxy_to_dict(box),
                detected_at=utc_now(),
                frame_path=frame_path,
                track_id=track_id,
            )
        except Exception:
            logger.exception("DB log insert failed for person_id=%d.", person_id)

        logger.info(
            "🔔 Detection notified | person_id=%d (%s) | camera_id=%d | score=%.3f",
            person_id, person_name, camera_id, score,
        )
        return True

    def reset_cooldown(self, person_id: int, camera_id: int) -> None:
        with self._cooldown_lock:
            self._cooldown_map.pop((person_id, camera_id), None)

    def reset_all_cooldowns(self) -> None:
        with self._cooldown_lock:
            self._cooldown_map.clear()
        logger.debug("All notification cooldowns cleared.")

    def _cooldown_check(self, person_id: int, camera_id: int) -> bool:
        key = (person_id, camera_id)
        now = time.monotonic()

        with self._cooldown_lock:
            last = self._cooldown_map.get(key, 0.0)
            if now - last < self._cooldown:
                return False
            self._cooldown_map[key] = now
            return True
