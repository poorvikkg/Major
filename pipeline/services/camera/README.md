# pipeline/services/camera

## Purpose
Multi-camera RTSP streaming management with threaded readers and processors.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `camera_manager.py` | ~160 | Public facade for managing multiple streams via a central registry. |
| `stream_processor.py` | ~140 | Coordinates one stream, spawning reader and processor threads. |
| `frame_reader.py` | ~90 | Dedicated RTSP reader loop with exponential back-off reconnection. |
| `processor_thread.py` | ~90 | Applies frame skip, runs FaceInference, updates tracker, and notifies. |
| `camera_registry.py` | ~40 | Thread-safe dictionary of active `StreamProcessor` instances. |
| `frame_buffer.py` | ~40 | Ring buffer dropping old frames to ensure the processor isn't delayed. |
| `models.py` | ~20 | Enums and Dataclasses (`StreamConfig`, `StreamState`). |
