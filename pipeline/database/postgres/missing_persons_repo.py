"""
missing_persons_repo.py
-----------------------
Repository methods for missing persons.
"""

import logging
from typing import Dict, List, Optional

from pipeline.database import queries
from pipeline.database.postgres.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class MissingPersonsRepository(BaseRepository):
    def get_all_missing_persons(self) -> List[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_ALL_MISSING_PERSONS)
            rows = cur.fetchall()

        result = [self._serialize_row(row) for row in rows]
        logger.debug("get_all_missing_persons → %d records.", len(result))
        return result

    def get_missing_person_by_id(self, person_id: int) -> Optional[Dict]:
        with self._connect() as cur:
            cur.execute(queries.GET_MISSING_PERSON_BY_ID, (person_id,))
            row = cur.fetchone()

        if row is None:
            logger.warning("get_missing_person_by_id: id=%d not found.", person_id)
            return None
        return self._serialize_row(row)

    def get_person_image_paths(self, person_id: int) -> List[str]:
        with self._connect() as cur:
            cur.execute(queries.GET_PERSON_IMAGE_PATHS, (person_id,))
            rows = cur.fetchall()

        paths = [row["image_url"] for row in rows]
        logger.debug("get_person_image_paths: person_id=%d → %d path(s).", person_id, len(paths))
        return paths

    def get_missing_persons_paginated(self, limit: int = 50, offset: int = 0) -> Dict:
        with self._connect() as cur:
            cur.execute(queries.GET_MISSING_PERSONS_PAGINATED, (limit, offset))
            rows = cur.fetchall()

            cur.execute(queries.COUNT_ACTIVE_MISSING_PERSONS)
            total = cur.fetchone()["total"]

        return {
            "items":  [self._serialize_row(r) for r in rows],
            "total":  total,
            "limit":  limit,
            "offset": offset,
        }

    def count_active_missing_persons(self) -> int:
        with self._connect() as cur:
            cur.execute(queries.COUNT_ACTIVE_MISSING_PERSONS)
            row = cur.fetchone()
        return int(row["total"])
