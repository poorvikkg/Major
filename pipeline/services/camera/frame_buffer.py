"""
frame_buffer.py
---------------
Purpose  : Thread-safe ring buffer for video frames.
Inputs   : Frames and their indices.
Outputs  : The latest frames.
Raises   : queue.Empty on timeout.

Single Responsibility: Safely pass frames between reader and processor threads,
dropping the oldest frame if the processor falls behind.
"""

import queue
from typing import Tuple, Optional
import numpy as np


class FrameBuffer:
    """
    A thread-safe queue that drops the oldest item when full.
    Prefers fresh frames over processing every single delayed frame.
    """
    def __init__(self, maxsize: int = 4):
        self._queue = queue.Queue(maxsize=maxsize)

    def put_latest(self, frame_idx: int, frame: np.ndarray) -> None:
        """Put a new frame into the buffer, dropping the oldest if full."""
        try:
            self._queue.put_nowait((frame_idx, frame))
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait((frame_idx, frame))
            except queue.Full:
                pass

    def get(self, timeout: float = 1.0) -> Tuple[int, np.ndarray]:
        """
        Get the next frame.
        Raises queue.Empty if nothing is available within the timeout.
        """
        return self._queue.get(timeout=timeout)
