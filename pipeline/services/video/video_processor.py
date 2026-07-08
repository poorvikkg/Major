"""
video_processor.py
------------------
Purpose  : Orchestrates inference over uploaded video files.
Inputs   : Video path, FaceInference, Database, Notifier.
Outputs  : DetectionReport.
Raises   : N/A (returns a failed DetectionReport on error).

Single Responsibility: Coordinate cv2 reading, inference, and deduplication
for a static video file.
"""

import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np

from pipeline.services.inference import FaceInference, InferenceResult
from pipeline.services.notifier import Notifier
from pipeline.services.api import BackendSocketClient
from pipeline.services.utils import save_frame, xyxy_to_dict, draw_detection
from pipeline.database.postgres import PostgresRepository
from pipeline.config import get_config

from pipeline.services.video.detection_report import DetectionReport, VideoDetection
from pipeline.services.video.video_deduplicator import VideoDeduplicator

logger = logging.getLogger(__name__)

_SUPPORTED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


class VideoProcessor:
    """
    Processes uploaded video files and returns a DetectionReport.
    """

    def __init__(
        self,
        inference:     FaceInference,
        db_repo:       PostgresRepository,
        notifier:      Optional[Notifier]              = None,
        socket_client: Optional[BackendSocketClient]   = None,
        frame_interval: int  = 30,
        dedup_window:   int  = 90,
        save_frames:    bool = True,
    ) -> None:
        self._inference      = inference
        self._db             = db_repo
        self._notifier       = notifier
        self._socket         = socket_client
        self._frame_interval = max(frame_interval, 1)
        self._dedup_window   = dedup_window
        self._save_frames    = save_frames
        self._name_cache: Dict[int, str] = {}

    def process(
        self,
        video_path:  str,
        camera_id:   int = 0,
        cancel_event: Optional[object] = None,
    ) -> DetectionReport:
        job_id = str(uuid.uuid4())[:8]
        path = Path(video_path)
        start_ts = time.monotonic()

        if not path.exists():
            return self._failed_report(job_id, str(path), f"File not found: {path}")
        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            return self._failed_report(
                job_id, str(path),
                f"Unsupported format '{path.suffix}'. Supported: {_SUPPORTED_EXTENSIONS}",
            )

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return self._failed_report(job_id, str(path), "cv2.VideoCapture failed to open file.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        duration = total_frames / fps

        detections: List[VideoDetection] = []
        frames_processed = 0
        dedup = VideoDeduplicator(self._dedup_window)

        try:
            frame_idx = 0
            while True:
                if cancel_event is not None and cancel_event.is_set():
                    return self._build_report(
                        job_id, str(path), "cancelled", total_frames, frames_processed,
                        duration, fps, detections, time.monotonic() - start_ts
                    )

                ret, frame = cap.read()
                if not ret:
                    break

                frame_idx += 1
                if frame_idx % self._frame_interval != 0:
                    continue

                frames_processed += 1
                timestamp_in_video = frame_idx / fps

                results: List[InferenceResult] = self._inference.run(frame)
                for result in results:
                    if not result.is_match or result.person_id is None:
                        continue

                    pid = result.person_id
                    if dedup.is_duplicate(pid, frame_idx):
                        continue

                    name = self._resolve_name(pid)
                    frame_path = self._process_match(job_id, pid, frame_idx, frame, result, name)

                    detections.append(VideoDetection(
                        person_id=pid, person_name=name, score=result.score,
                        bounding_box=xyxy_to_dict(result.box), frame_number=frame_idx,
                        timestamp_in_video=timestamp_in_video, frame_path=frame_path,
                    ))

                    if self._notifier:
                        self._notifier.notify(
                            person_id=pid, person_name=name, camera_id=camera_id,
                            score=result.score, box=result.box, track_id=None, frame=frame
                        )

                if total_frames > 0:
                    progress = (frame_idx / total_frames) * 100
                    if frames_processed % max(total_frames // (self._frame_interval * 20), 1) == 0:
                        self._emit_progress(job_id, progress, "processing")

        except Exception as e:
            logger.exception("Job %s failed during frame processing.", job_id)
            cap.release()
            return self._failed_report(job_id, str(path), f"Error: {str(e)}")
        finally:
            cap.release()

        processing_time = time.monotonic() - start_ts
        self._emit_progress(job_id, 100.0, "completed")
        return self._build_report(
            job_id, str(path), "completed", total_frames, frames_processed,
            duration, fps, detections, processing_time
        )

    def _process_match(
        self, job_id: str, pid: int, frame_idx: int,
        frame: np.ndarray, result: InferenceResult, name: str
    ) -> Optional[str]:
        if not self._save_frames:
            return None
        annotated = draw_detection(frame, result.box, name, result.score)
        return save_frame(
            annotated, directory=get_config().paths.uploads_images_dir,
            filename=f"vid_{job_id}_{pid}_{frame_idx}"
        )

    def _resolve_name(self, person_id: int) -> str:
        if person_id not in self._name_cache:
            try:
                rec = self._db.get_missing_person_by_id(person_id)
                self._name_cache[person_id] = rec["name"] if rec else "Unknown"
            except Exception:
                self._name_cache[person_id] = "Unknown"
        return self._name_cache[person_id]

    def _emit_progress(self, job_id: str, progress: float, status: str) -> None:
        if self._socket:
            try:
                self._socket.emit_video_progress(job_id, progress, status)
            except Exception:
                pass

    @staticmethod
    def _build_report(
        job_id, path, status, total_frames, frames_processed,
        duration, fps, detections, processing_time, error=None,
    ) -> DetectionReport:
        return DetectionReport(
            job_id=job_id, video_path=path, status=status, total_frames=total_frames,
            frames_processed=frames_processed, duration_seconds=duration, fps=fps,
            detections=detections, processing_time=processing_time, error=error
        )

    @staticmethod
    def _failed_report(job_id: str, path: str, error: str) -> DetectionReport:
        return DetectionReport(
            job_id=job_id, video_path=path, status="failed", total_frames=0,
            frames_processed=0, duration_seconds=0.0, fps=0.0, error=error
        )
