# AI Pipeline

Production-ready face detection, recognition, tracking, and notification pipeline for the missing person surveillance system.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AI Pipeline                                 │
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
│  │ CameraManager│   │VideoProcessor│   │   RecognitionService     │ │
│  │  (RTSP)      │   │ (Upload)     │   │  (Register / Delete)     │ │
│  └──────┬───────┘   └──────┬───────┘   └────────────┬─────────────┘ │
│         │                  │                         │               │
│         └────────┬─────────┘                         │               │
│                  ▼                                   │               │
│         ┌────────────────┐                           │               │
│         │  FaceInference │◄──────────────────────────┘               │
│         │  (Detector +   │                                           │
│         │  Recognizer +  │                                           │
│         │  FAISS search) │                                           │
│         └────────┬───────┘                                           │
│                  │                                                   │
│                  ▼                                                   │
│         ┌────────────────┐   ┌─────────────┐   ┌──────────────────┐ │
│         │  FaceTracker   │   │   Notifier  │──►│ BackendHTTPClient│ │
│         │  (ByteTrack)   │   │  (Cooldown) │   │ /api/detection   │ │
│         └────────────────┘   └──────┬──────┘   └──────────────────┘ │
│                                     │                                │
│                              ┌──────┴──────┐   ┌──────────────────┐ │
│                              │  PostgreSQL  │   │ Socket.IO client │ │
│                              │  (DB log)   │   │ detection_alert  │ │
│                              └─────────────┘   └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Module Reference

| Module | Location | Role |
|--------|----------|------|
| `preprocessing.py` | services/ | Image normalization, letterbox, face alignment |
| `postprocessing.py` | services/ | SCRFD decode, NMS, L2 normalize, cosine similarity |
| `detector.py` | services/ | SCRFD ONNX face detector |
| `recognizer.py` | services/ | ArcFace R100 ONNX recognizer (512-d embeddings) |
| `tracker.py` | services/ | ByteTrack multi-person tracker (self-contained Kalman) |
| `inference.py` | services/ | Per-frame: detect → align → embed → FAISS search |
| `embedding_manager.py` | services/ | Registration: multi-image → average → normalize → .npy |
| `faiss_manager.py` | services/ | IndexFlatIP cosine search, incremental CRUD |
| `camera_manager.py` | services/ | Manages N RTSP StreamProcessors |
| `stream_processor.py` | services/ | Single RTSP stream: dual-thread read/process, reconnect |
| `video_processor.py` | services/ | Video file: frame extraction, inference, DetectionReport |
| `api.py` | services/ | HTTP client + Socket.IO client for Node.js backend |
| `notifier.py` | services/ | Cooldown-gated notification dispatcher |
| `camera_service.py` | services/ | Camera CRUD service layer |
| `recognition_service.py` | services/ | Registration + FAISS sync service layer |
| `tracking_service.py` | services/ | Tracker lifecycle service layer |
| `notification_service.py` | services/ | Bulk notify, history, status |
| `utils.py` | services/ | Timestamps, bbox helpers, frame I/O, Base64 |
| `connection.py` | database/ | PostgreSQL connection pool singleton |
| `queries.py` | database/ | All SQL as named string constants |
| `postgres.py` | database/ | PostgresRepository: get/insert operations |
| `detector_loader.py` | loaders/ | Singleton SCRFD session (double-checked lock) |
| `recognizer_loader.py` | loaders/ | Singleton ArcFace session |
| `tracker_loader.py` | loaders/ | Per-stream tracker registry |

---

## Quick Start

### 1. Environment Variables

Copy `.env.example` (or create `.env` in the project root):

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=missing_persons
DB_USER=postgres
DB_PASSWORD=your_password
DB_MIN_CONN=2
DB_MAX_CONN=10

# Backend (Node.js)
BACKEND_URL=http://localhost:5000
BACKEND_API_KEY=your_api_key
SOCKET_URL=http://localhost:5000
BACKEND_TIMEOUT=5
BACKEND_RETRIES=3
```

### 2. Place Model Files

```
models/
  face_detection/
    scrfd_10g_bnkps.onnx        ← Download from InsightFace
  face_recognition/
    arcface_r100_finetuned.onnx ← Your fine-tuned model
```

### 3. Install Dependencies

```bash
pip install -r pipeline/requirements.txt
```

### 4. Register a Missing Person

```python
from dotenv import load_dotenv
load_dotenv()

from pipeline.loaders.detector_loader   import get_detector
from pipeline.loaders.recognizer_loader import get_recognizer
from pipeline.services.embedding_manager import EmbeddingManager
from pipeline.services.faiss_manager     import FAISSManager
from pipeline.services.recognition_service import RecognitionService
from pipeline.services.inference         import FaceInference
from pipeline.database.postgres          import PostgresRepository

detector   = get_detector()
recognizer = get_recognizer()
faiss_mgr  = FAISSManager()
db_repo    = PostgresRepository()
emb_mgr    = EmbeddingManager(detector, recognizer)
inference  = FaceInference(detector, recognizer, faiss_mgr)

rec_svc = RecognitionService(emb_mgr, faiss_mgr, inference, db_repo)
result  = rec_svc.register_person(
    person_id=42,
    image_paths=["data/registered_faces/42/img1.jpg",
                 "data/registered_faces/42/img2.jpg"],
)
print(result)
```

### 5. Start Live CCTV Monitoring

```python
from pipeline.services.camera_manager import CameraManager
from pipeline.services.faiss_manager  import FAISSManager
from pipeline.database.postgres        import PostgresRepository

faiss_mgr = FAISSManager()
db_repo   = PostgresRepository()
mgr       = CameraManager(faiss_mgr=faiss_mgr, db_repo=db_repo)

mgr.register_signal_handlers()
mgr.load_cameras_from_db()
mgr.start_all()

# Block until SIGTERM
import signal, time
signal.pause()
```

### 6. Process a Video Upload

```python
from pipeline.services.video_processor import VideoProcessor
from pipeline.services.inference       import FaceInference
from pipeline.database.postgres        import PostgresRepository

processor = VideoProcessor(inference=inference, db_repo=db_repo)
report    = processor.process("data/uploads/videos/footage.mp4", camera_id=1)
print(report.to_dict())
```

### 7. Run Tests

```bash
cd pipeline
pytest tests/ -v --cov=pipeline --cov-report=term-missing
```

---

## Docker

### Build

```bash
docker build -t ai-pipeline:latest ./pipeline
```

### Run with volumes

```bash
docker run \
  --env-file .env \
  --gpus all \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/data:/app/data \
  ai-pipeline:latest \
  python -m pipeline.main
```

---

## Performance Notes

| Component | Typical latency (CPU) | GPU speedup |
|-----------|----------------------|-------------|
| SCRFD-10G detect (640×640) | ~80ms | ~10ms |
| ArcFace R100 embed (112×112) | ~40ms | ~5ms |
| FAISS IndexFlatIP search (10k persons) | <1ms | — |
| ByteTrack association (20 tracks) | <1ms | — |
| **Full frame pipeline** | **~120ms (~8 FPS)** | **~15ms (~65 FPS)** |

- **Frame skip** (default: every 3rd frame) triples effective throughput.
- **Batch embedding** is used when multiple faces appear in the same frame.
- **Cooldown** (default: 30s per person/camera) prevents notification floods.

---

## Key Design Decisions

### Single Responsibility
Each module has one axis of change: `detector.py` only does detection, `notifier.py` only dispatches notifications, etc.

### Dependency Injection
`CameraManager`, `VideoProcessor`, and `RecognitionService` all accept their dependencies via constructor injection — making unit testing trivial with mocks.

### Zero Unnecessary Rebuilds
FAISS `add_person()` never rebuilds the index (O(1)). Only `delete_person()` and `update_person()` require a rebuild, and these are rare admin operations.

### Atomic Disk Writes
All `.npy`, `.pkl`, and `.json` files are written using temp-file + atomic rename to prevent corruption on crash.

### Thread Safety
- FAISS reads: concurrent via `threading.RLock`.
- Notifier cooldown map: `threading.Lock`.
- Camera registry: `threading.RLock`.
- Model loaders: double-checked locking (lock-free hot path).
