"""
camera_manager.py
-----------------
Purpose  : Public manager facade for Multi-camera RTSP streaming.
Inputs   : FAISSManager, PostgresRepository, global configs.
Outputs  : Spawns/stops stream processors.
Raises   : N/A

Single Responsibility: Provide a unified interface to add, start, stop,
and query metrics for multiple camera streams.
"""

import logging
import signal
from typing import Dict, List, Optional

from pipeline.loaders.detector_loader   import get_detector
from pipeline.loaders.recognizer_loader import get_recognizer
from pipeline.loaders.tracker_loader    import get_tracker, release_tracker

from pipeline.services.inference        import FaceInference
from pipeline.services.faiss.faiss_manager import FAISSManager
from pipeline.services.notifier         import Notifier
from pipeline.services.api              import get_http_client, get_socket_client

from pipeline.database.postgres         import PostgresRepository

from pipeline.services.camera.models import StreamConfig
from pipeline.services.camera.camera_registry import CameraRegistry
from pipeline.services.camera.stream_processor import StreamProcessor

logger = logging.getLogger(__name__)


class CameraManager:
    """
    Manages all RTSP camera stream processors.
    """

    def __init__(
        self,
        faiss_mgr:             FAISSManager,
        db_repo:               PostgresRepository,
        recognition_threshold: float = 0.45,
        frame_skip:            int   = 3,
        cooldown_sec:          int   = 30,
        save_frames:           bool  = True,
        include_frame_b64:     bool  = False,
    ) -> None:
        self._faiss = faiss_mgr
        self._db = db_repo
        self._registry = CameraRegistry()

        # Build shared dependencies once
        detector   = get_detector()
        recognizer = get_recognizer()
        self._inference = FaceInference(
            detector=detector,
            recognizer=recognizer,
            faiss_mgr=faiss_mgr,
            threshold=recognition_threshold,
        )
        self._http_client   = get_http_client()
        self._socket_client = get_socket_client()
        self._notifier = Notifier(
            http_client=self._http_client,
            socket_client=self._socket_client,
            db_repo=db_repo,
            cooldown_sec=cooldown_sec,
            save_frames=save_frames,
            include_frame_b64=include_frame_b64,
        )
        self._frame_skip: int = frame_skip

        # Connect Socket.IO (best-effort)
        try:
            self._socket_client.connect()
        except Exception:
            logger.warning("Socket.IO initial connect failed — will retry on first emit.")

        logger.info("CameraManager initialised.")

    def load_cameras_from_db(self) -> int:
        cameras = self._db.get_active_cameras()
        count = 0
        for cam in cameras:
            self.add_camera(
                camera_id=cam["id"],
                stream_url=cam["stream_url"],
            )
            count += 1
        logger.info("Loaded %d active camera(s) from DB.", count)
        return count

    def add_camera(
        self,
        camera_id:  int,
        stream_url: str,
        frame_skip: Optional[int] = None,
        **config_kwargs,
    ) -> bool:
        config = StreamConfig(
            camera_id=camera_id,
            stream_url=stream_url,
            frame_skip=frame_skip if frame_skip is not None else self._frame_skip,
            **config_kwargs,
        )
        tracker   = get_tracker(stream_id=f"cam_{camera_id}")
        processor = StreamProcessor(
            config=config,
            inference=self._inference,
            notifier=self._notifier,
            db_repo=self._db,
            tracker=tracker,
            socket_client=self._socket_client,
        )
        if self._registry.add(camera_id, processor):
            logger.info("Camera %d registered | url=%s", camera_id, stream_url)
            return True
        return False

    def remove_camera(self, camera_id: int) -> bool:
        proc = self._registry.remove(camera_id)
        if proc is None:
            logger.warning("remove_camera: camera_id=%d not registered.", camera_id)
            return False

        proc.stop()
        release_tracker(f"cam_{camera_id}")
        logger.info("Camera %d removed.", camera_id)
        return True

    def start_camera(self, camera_id: int) -> bool:
        proc = self._registry.get(camera_id)
        if proc is None:
            logger.error("start_camera: camera_id=%d not registered.", camera_id)
            return False
        proc.start()
        return True

    def stop_camera(self, camera_id: int) -> bool:
        proc = self._registry.get(camera_id)
        if proc is None:
            logger.error("stop_camera: camera_id=%d not registered.", camera_id)
            return False
        proc.stop()
        return True

    def start_all(self) -> int:
        started = 0
        for proc in self._registry.get_all():
            proc.start()
            started += 1
        logger.info("Started %d camera stream(s).", started)
        return started

    def stop_all(self) -> int:
        camera_ids = self._registry.get_all_ids()
        stopped = 0
        for cid in camera_ids:
            self.stop_camera(cid)
            stopped += 1

        self._socket_client.disconnect()
        self._http_client.close()
        logger.info("Stopped %d camera stream(s).", stopped)
        return stopped

    def get_metrics(self) -> List[Dict]:
        return [p.get_metrics() for p in self._registry.get_all()]

    def get_active_camera_ids(self) -> List[int]:
        return [p.camera_id for p in self._registry.get_all() if p.is_running]

    def register_signal_handlers(self) -> None:
        def _handler(signum, frame):
            logger.info("Signal %d received — shutting down CameraManager …", signum)
            self.stop_all()

        signal.signal(signal.SIGTERM, _handler)
        signal.signal(signal.SIGINT,  _handler)
        logger.info("Signal handlers registered (SIGTERM / SIGINT).")
