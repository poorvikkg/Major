"""
camera_registry.py
------------------
Purpose  : Thread-safe registry for active StreamProcessors.
Inputs   : Camera IDs and StreamProcessor instances.
Outputs  : Registered streams.
Raises   : N/A

Single Responsibility: Manage the dictionary of active camera streams.
"""

import logging
import threading
from typing import Dict, List, Optional

from pipeline.services.camera.stream_processor import StreamProcessor

logger = logging.getLogger(__name__)


class CameraRegistry:
    """Thread-safe storage for active camera streams."""

    def __init__(self):
        self._processors: Dict[int, StreamProcessor] = {}
        self._lock = threading.RLock()

    def add(self, camera_id: int, processor: StreamProcessor) -> bool:
        """Add a processor if not already registered."""
        with self._lock:
            if camera_id in self._processors:
                logger.warning("Camera %d is already registered.", camera_id)
                return False
            self._processors[camera_id] = processor
            return True

    def remove(self, camera_id: int) -> Optional[StreamProcessor]:
        """Remove and return a processor if found."""
        with self._lock:
            return self._processors.pop(camera_id, None)

    def get(self, camera_id: int) -> Optional[StreamProcessor]:
        with self._lock:
            return self._processors.get(camera_id)

    def get_all(self) -> List[StreamProcessor]:
        with self._lock:
            return list(self._processors.values())

    def get_all_ids(self) -> List[int]:
        with self._lock:
            return list(self._processors.keys())
