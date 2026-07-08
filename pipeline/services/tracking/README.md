# pipeline/services/tracking

## Purpose
ByteTrack-style multi-face tracker, split into single-responsibility modules.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `track_state.py` | ~80 | `TrackState` enum, `Track` dataclass — **data models only** |
| `kalman_filter.py` | ~75 | `KalmanBoxTracker` — **Kalman math only** |
| `iou_utils.py` | ~55 | `compute_iou()` — **IoU math only** |
| `association.py` | ~60 | `greedy_match()` — **cost-matrix matching only** |
| `tracker.py` | ~195 | `FaceTracker` — **lifecycle orchestration only** |

## Why Split?

| Old file | Lines | Problem |
|----------|-------|---------|
| `tracker.py` | 356 | Kalman + IoU + assignment + state + lifecycle all mixed |

Each extracted module is independently testable and replaceable.  
For example, swapping to Hungarian assignment requires touching only `association.py`.

## Key Design Decisions

- **No external dependencies** — custom Kalman avoids `filterpy`/`scipy`.
- **One tracker per stream** — `FaceTracker` is not thread-safe by design;  
  `CameraManager` creates one per stream via `tracker_loader`.
- **Two-pass association** — matches high-confidence detections to Active  
  tracks first, then low-confidence to Lost tracks.

## How It Interacts

```
FaceDetector  →  List[DetectionResult]
                       │
                       ▼
               FaceTracker.update()
                  │         │
                  │         ▼
                  │    compute_iou()   ← iou_utils.py
                  │    greedy_match()  ← association.py
                  │    Track.advance() ← Kalman predict ← kalman_filter.py
                  │    Track.mark_updated()
                  ▼
         List[Track]  →  StreamProcessor / VideoProcessor
```

## Usage

```python
from pipeline.services.tracking import FaceTracker

tracker = FaceTracker(max_age=30, min_hits=3, iou_threshold=0.3)

for frame in stream:
    detections = detector.detect_faces(frame)
    tracks = tracker.update(detections)
    for t in tracks:
        print(t.track_id, t.box)
```
