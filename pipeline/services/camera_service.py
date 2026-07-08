"""
camera_service.py
-----------------
Service layer for camera CRUD operations.

Wraps PostgresRepository camera methods with business logic:
- Validates camera data before inserting
- Provides helpers used by CameraManager during stream lifecycle

This keeps CameraManager free of direct SQL concerns.
"""

import logging
from typing import Dict, List, Optional

from pipeline.database.postgres import PostgresRepository

logger = logging.getLogger(__name__)


class CameraService:
    """
    High-level camera operations for the AI pipeline.

    Parameters
    ----------
    db_repo : Injected PostgresRepository.
    """

    def __init__(self, db_repo: PostgresRepository) -> None:
        self._db = db_repo

    def get_all_cameras(self) -> List[Dict]:
        """Return all cameras (active and inactive)."""
        return self._db.get_all_cameras()

    def get_active_cameras(self) -> List[Dict]:
        """Return only is_active=TRUE cameras with stream URLs."""
        cameras = self._db.get_active_cameras()
        logger.debug("CameraService: %d active camera(s) fetched.", len(cameras))
        return cameras

    def get_camera(self, camera_id: int) -> Optional[Dict]:
        """
        Return camera details by ID.

        Returns
        -------
        Camera dict or None if not found.
        """
        camera = self._db.get_camera_by_id(camera_id)
        if camera is None:
            logger.warning("CameraService: camera_id=%d not found.", camera_id)
        return camera

    def validate_stream_url(self, stream_url: str) -> bool:
        """
        Basic stream URL validation.

        Accepted protocols: rtsp://, rtmp://, http://, https://, file paths.

        Returns
        -------
        True if the URL format looks valid.
        """
        lower = stream_url.strip().lower()
        valid_prefixes = ("rtsp://", "rtmp://", "http://", "https://", "/", "./")
        is_valid = any(lower.startswith(p) for p in valid_prefixes)
        if not is_valid:
            logger.warning("Invalid stream URL: '%s'", stream_url)
        return is_valid

    def build_stream_configs(self) -> List[Dict]:
        """
        Return active cameras formatted as StreamConfig-compatible dicts
        for CameraManager.add_camera() calls.
        """
        cameras = self.get_active_cameras()
        configs = []
        for cam in cameras:
            url = cam.get("stream_url", "")
            if not url or not self.validate_stream_url(url):
                logger.warning(
                    "Skipping camera_id=%d — missing or invalid stream_url.", cam["id"]
                )
                continue
            configs.append({
                "camera_id":  cam["id"],
                "stream_url": url,
            })
        return configs
