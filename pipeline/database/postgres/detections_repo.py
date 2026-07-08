"""
detections_repo.py
------------------
Repository methods for detection logs.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from pipeline.database import queries
from pipeline.database.postgres.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class DetectionsRepository(BaseRepository):
    def insert_detection_log(
        self,
        person_id:        int,
        camera_id:        int,
        similarity_score: float,
        bounding_box:     Dict,
        detected_at:      datetime,
        frame_path:       Optional[str] = None,
        track_id:         Optional[int] = None,
    ) -> int:
        bbox_json = json.dumps(bounding_box)

        with self._connect() as cur:
            cur.execute(
                queries.INSERT_DETECTION_LOG,
                (
                    person_id,
                    camera_id,
                    round(float(similarity_score), 6),
                    bbox_json,
                    detected_at,
                    frame_path,
                    track_id,
                ),
            )
            row = cur.fetchone()
            cur.connection.commit()

        new_id = int(row["id"])
        logger.info(
            "Detection log inserted | id=%d | person_id=%d | camera_id=%d | score=%.4f",
            new_id, person_id, camera_id, similarity_score,
        )
        return new_id

    def get_detection_logs_by_person(self, person_id: int, limit: int = 100) -> List[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_DETECTION_LOGS_BY_PERSON, (person_id, limit))
            rows = cur.fetchall()

        result = [self._serialize_row(r) for r in rows]
        logger.debug("get_detection_logs_by_person: person_id=%d → %d log(s).", person_id, len(result))
        return result

    def get_detection_logs_by_camera(self, camera_id: int, limit: int = 100) -> List[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_DETECTION_LOGS_BY_CAMERA, (camera_id, limit))
            rows = cur.fetchall()

        result = [self._serialize_row(r) for r in rows]
        logger.debug("get_detection_logs_by_camera: camera_id=%d → %d log(s).", camera_id, len(result))
        return result

    def get_recent_detections(self, limit: int = 50) -> List[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_RECENT_DETECTIONS, (limit,))
            rows = cur.fetchall()

        result = [self._serialize_row(r) for r in rows]
        logger.debug("get_recent_detections → %d record(s).", len(result))
        return result

    def get_detection_log_by_id(self, log_id: int) -> Optional[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_DETECTION_LOG_BY_ID, (log_id,))
            row = cur.fetchone()

        if row is None:
            logger.warning("get_detection_log_by_id: id=%d not found.", log_id)
            return None
        return self._serialize_row(row)

    def count_detections_for_person_today(self, person_id: int) -> int:
        with self._connect() as cur:
            cur.execute(queries.COUNT_DETECTIONS_FOR_PERSON_TODAY, (person_id,))
            row = cur.fetchone()
        return int(row["total"])
