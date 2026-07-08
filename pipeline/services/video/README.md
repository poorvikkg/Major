# pipeline/services/video

## Purpose
Process uploaded video files in batch mode, generating a `DetectionReport`.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `video_processor.py` | ~150 | Orchestrates the video decoding, frame-skipping, inference, and deduplication logic. |
| `detection_report.py` | ~60 | Data structures defining what a match looks like (`VideoDetection`) and what the final output is (`DetectionReport`). |
| `video_deduplicator.py` | ~30 | Handles tracking the last seen frame for a `person_id` to prevent rapid duplicate reports. |
