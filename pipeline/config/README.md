# pipeline/config

## Purpose
Central configuration for the entire AI pipeline.  
**No threshold, path, or timeout is hardcoded anywhere else in the codebase.**

## Files

| File | Responsibility |
|------|----------------|
| `pipeline_config.json` | Single source of truth for all configurable values |
| `loader.py` | Loads JSON → typed frozen dataclasses; singleton via `lru_cache` |
| `__init__.py` | Exposes public API |

## How It Works

```python
from pipeline.config import get_config

cfg = get_config()                      # cached after first call
threshold = cfg.inference.recognition_threshold
model_path = cfg.detector.model_path
```

## Hot Reload

```python
from pipeline.config import reload_config

cfg = reload_config()  # clears cache, re-reads JSON
```

## Config Sections

| Section | Purpose |
|---------|---------|
| `detector` | SCRFD model path, NMS/confidence thresholds, input size |
| `recognizer` | ArcFace model path, embedding dim, batch size |
| `tracker` | ByteTrack max_age, min_hits, IoU threshold, confidence bands |
| `inference` | Recognition threshold, FAISS top-k |
| `stream` | Frame skip, reconnect delay, buffer size, FPS cap |
| `video` | Frame interval, dedup window, supported extensions |
| `notification` | Cooldown, frame saving, JPEG quality |
| `faiss` | Index directory, search threshold |
| `embeddings` | Store directory, embedding dimension |
| `paths` | Upload, temp, registered faces directories |
| `backend` | Node.js URL, Socket.IO URL, API key, timeout |

## Interaction with Other Modules

- **Loaders** (`loaders/`) read model paths from `cfg.detector.model_path` and `cfg.recognizer.model_path`
- **FaceTracker** reads `cfg.tracker.*`
- **FAISSManager** reads `cfg.faiss.*`
- **Notifier** reads `cfg.notification.*`
- **StreamProcessor** reads `cfg.stream.*`
- **VideoProcessor** reads `cfg.video.*`
