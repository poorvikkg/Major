"""
notification_service.py
-----------------------
High-level notification orchestration service.

Wraps Notifier with:
- Bulk notification dispatch (for video upload reports)
- Alert history retrieval from PostgreSQL
- Cooldown management API (expose reset capability to admin endpoints)
- Status checks (HTTP backend reachability, Socket.IO connection status)
"""

import logging
from typing import Dict, List, Optional

import numpy as np

from pipeline.services.notifier      import Notifier
from pipeline.services.api           import BackendHTTPClient, BackendSocketClient
from pipeline.services.video_processor import DetectionReport
from pipeline.database.postgres       import PostgresRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Orchestrates notification dispatch and history retrieval.

    Parameters
    ----------
    notifier      : Injected Notifier (owns HTTP + Socket.IO + DB write).
    http_client   : BackendHTTPClient for health checks.
    socket_client : BackendSocketClient for connection status.
    db_repo       : PostgresRepository for history queries.
    """

    def __init__(
        self,
        notifier:      Notifier,
        http_client:   BackendHTTPClient,
        socket_client: BackendSocketClient,
        db_repo:       PostgresRepository,
    ) -> None:
        self._notifier = notifier
        self._http     = http_client
        self._socket   = socket_client
        self._db       = db_repo
        logger.info("NotificationService initialised.")

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def notify_match(
        self,
        person_id:   int,
        person_name: str,
        camera_id:   int,
        score:       float,
        box:         np.ndarray,
        track_id:    Optional[int] = None,
        frame:       Optional[np.ndarray] = None,
    ) -> bool:
        """
        Dispatch a single detection notification.

        Returns True if dispatched (not suppressed by cooldown).
        """
        return self._notifier.notify(
            person_id=person_id,
            person_name=person_name,
            camera_id=camera_id,
            score=score,
            box=box,
            track_id=track_id,
            frame=frame,
        )

    def notify_from_report(
        self,
        report:    DetectionReport,
        camera_id: int = 0,
    ) -> int:
        """
        Dispatch notifications for all unique persons found in a video report.

        Only the first detection per unique person_id in the report is dispatched
        (deduplication already happened inside VideoProcessor).

        Parameters
        ----------
        report    : DetectionReport from VideoProcessor.process().
        camera_id : Camera ID to associate the notifications with.

        Returns
        -------
        Number of notifications dispatched.
        """
        seen: set = set()
        dispatched = 0

        for det in report.detections:
            if det.person_id in seen:
                continue
            seen.add(det.person_id)

            sent = self._notifier.notify(
                person_id=det.person_id,
                person_name=det.person_name,
                camera_id=camera_id,
                score=det.score,
                box=np.array([
                    det.bounding_box["x1"],
                    det.bounding_box["y1"],
                    det.bounding_box["x2"],
                    det.bounding_box["y2"],
                ], dtype=np.float32),
                track_id=None,
            )
            if sent:
                dispatched += 1

        logger.info(
            "notify_from_report: %d unique person(s) | %d notification(s) dispatched.",
            len(seen), dispatched,
        )
        return dispatched

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """
        Retrieve the most recent detection log entries from the database.

        Returns
        -------
        List of detection log dicts (most recent first).
        """
        return self._db.get_recent_detections(limit=limit)

    def get_alerts_for_person(
        self,
        person_id: int,
        limit:     int = 100,
    ) -> List[Dict]:
        """Return detection log entries for a specific missing person."""
        return self._db.get_detection_logs_by_person(person_id, limit=limit)

    def get_alerts_for_camera(
        self,
        camera_id: int,
        limit:     int = 100,
    ) -> List[Dict]:
        """Return detection log entries for a specific camera."""
        return self._db.get_detection_logs_by_camera(camera_id, limit=limit)

    # ------------------------------------------------------------------
    # Cooldown management
    # ------------------------------------------------------------------

    def reset_cooldown(self, person_id: int, camera_id: int) -> None:
        """Clear the notification cooldown for a (person, camera) pair."""
        self._notifier.reset_cooldown(person_id, camera_id)
        logger.info("Cooldown cleared | person_id=%d | camera_id=%d", person_id, camera_id)

    def reset_all_cooldowns(self) -> None:
        """Clear all notification cooldowns (e.g., after a system restart)."""
        self._notifier.reset_all_cooldowns()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> Dict:
        """
        Return a status dict for monitoring endpoints.

        Returns
        -------
        {
            "backend_reachable": bool,
            "socket_connected": bool,
        }
        """
        return {
            "backend_reachable": self._http.health_check(),
            "socket_connected":  self._socket.is_connected,
        }
