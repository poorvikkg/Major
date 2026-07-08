"""
video_deduplicator.py
---------------------
Purpose  : Deduplicate face matches within a single video file.
Inputs   : Person ID, frame number, state dictionary.
Outputs  : Boolean (True if duplicate).
"""

from typing import Dict


class VideoDeduplicator:
    """
    Suppresses re-reporting the same person_id within a certain frame window.
    """

    def __init__(self, window: int):
        self._window = window
        self._last_seen: Dict[int, int] = {}

    def is_duplicate(self, person_id: int, frame_idx: int) -> bool:
        """
        Check if the person was already reported within the window.
        Updates the internal state if not a duplicate.
        """
        last = self._last_seen.get(person_id, -self._window - 1)
        if (frame_idx - last) < self._window:
            return True
        
        self._last_seen[person_id] = frame_idx
        return False
