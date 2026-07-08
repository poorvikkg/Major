"""
models.py
---------
Purpose  : Dataclasses and Enums for the camera module.
"""

from dataclasses import dataclass
from enum import Enum, auto


class StreamState(Enum):
    IDLE         = auto()
    CONNECTING   = auto()
    RUNNING      = auto()
    RECONNECTING = auto()
    STOPPED      = auto()


@dataclass
class StreamConfig:
    camera_id:           int
    stream_url:          str
    frame_skip:          int   = 3          # process 1 out of every N frames
    reconnect_delay:     float = 5.0        # seconds between reconnect attempts
    max_reconnect_tries: int   = 10         # 0 = infinite
    frame_buffer_size:   int   = 4          # ring buffer depth
    capture_width:       int   = 0          # 0 = use stream native resolution
    capture_height:      int   = 0
    fps_cap:             int   = 30         # max frames to read per second
