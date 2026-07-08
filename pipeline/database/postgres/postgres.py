"""
postgres.py
-----------
Facade combining all PostgreSQL repositories into a single PostgresRepository.
"""

import logging
from typing import Optional

from pipeline.database.postgres.base_repo import ConnectionFactory
from pipeline.database.postgres.missing_persons_repo import MissingPersonsRepository
from pipeline.database.postgres.cameras_repo import CamerasRepository
from pipeline.database.postgres.detections_repo import DetectionsRepository

logger = logging.getLogger(__name__)


class PostgresRepository(
    MissingPersonsRepository,
    CamerasRepository,
    DetectionsRepository,
):
    """
    Data access layer for the AI pipeline's PostgreSQL database.
    Combines missing persons, cameras, and detections repositories.
    """

    def __init__(self, connection_factory: Optional[ConnectionFactory] = None) -> None:
        super().__init__(connection_factory=connection_factory)
        logger.debug("PostgresRepository initialised.")
