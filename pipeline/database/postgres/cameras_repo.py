"""
cameras_repo.py
---------------
Repository methods for cameras.
"""

import logging
from typing import Dict, List, Optional

from pipeline.database import queries
from pipeline.database.postgres.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class CamerasRepository(BaseRepository):
    def get_all_cameras(self) -> List[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_ALL_CAMERAS)
            rows = cur.fetchall()

        result = [self._serialize_row(r) for r in rows]
        logger.debug("get_all_cameras → %d records.", len(result))
        return result

    def get_camera_by_id(self, camera_id: int) -> Optional[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_CAMERA_BY_ID, (camera_id,))
            row = cur.fetchone()

        if row is None:
            logger.warning("get_camera_by_id: id=%d not found.", camera_id)
            return None
        return self._serialize_row(row)

    def get_active_cameras(self) -> List[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_ACTIVE_CAMERAS)
            rows = cur.fetchall()

        result = [self._serialize_row(r) for r in rows]
        logger.debug("get_active_cameras → %d active camera(s).", len(result))
        return result
