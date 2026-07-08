# pipeline/services/detection

## Purpose
Face detection using SCRFD, split into single-responsibility modules.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `detection_result.py` | ~30 | Immutable `DetectionResult` dataclass. |
| `detector.py` | ~160 | `FaceDetector` — inference, ONNX session management, GPU fallback. |

## Why Split?

| Old file | Lines | Problem |
|----------|-------|---------|
| `detector.py` | 282 | Data models mixed with inference code. |

## How It Interacts

```
Camera / Video
      │ (BGR frame)
      ▼
 FaceDetector.detect_faces()  → Calls preprocessing.normalize_for_detector()
                              → Runs ONNX session
                              → Calls postprocessing.decode_scrfd_outputs()
      │
      ▼
 List[DetectionResult]        → Passed to tracker and recognizer.
```
