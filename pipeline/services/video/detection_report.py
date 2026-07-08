"""
detection_report.py
-------------------
Purpose  : Data models for video processing results.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class VideoDetection:
    """A single match event found in a video."""
    person_id:    int
    person_name:  str
    score:        float
    bounding_box: Dict
    frame_number: int
    timestamp_in_video: float   # seconds from video start
    frame_path:   Optional[str] = None


@dataclass
class DetectionReport:
    """Complete processing report for one video file."""
    job_id:           str
    video_path:       str
    status:           str            # 'completed' | 'failed' | 'cancelled'
    total_frames:     int
    frames_processed: int
    duration_seconds: float
    fps:              float
    detections:       List[VideoDetection] = field(default_factory=list)
    processing_time:  float = 0.0
    error:            Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "job_id":            self.job_id,
            "video_path":        self.video_path,
            "status":            self.status,
            "total_frames":      self.total_frames,
            "frames_processed":  self.frames_processed,
            "duration_seconds":  round(self.duration_seconds, 2),
            "fps":               round(self.fps, 2),
            "detections":        [
                {
                    "person_id":         d.person_id,
                    "person_name":       d.person_name,
                    "score":             round(d.score, 4),
                    "confidence":        f"{d.score * 100:.1f}%",
                    "bounding_box":      d.bounding_box,
                    "frame_number":      d.frame_number,
                    "timestamp_in_video": round(d.timestamp_in_video, 2),
                    "frame_path":        d.frame_path,
                }
                for d in self.detections
            ],
            "unique_persons_found": len({d.person_id for d in self.detections}),
            "processing_time_sec":  round(self.processing_time, 2),
            "error":                self.error,
        }
