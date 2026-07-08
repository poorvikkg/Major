# pipeline/services/api

## Purpose
Network clients for posting detections to the Node.js REST API and emitting real-time Socket.IO events.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `http_client.py` | ~80 | `requests`-based client for `POST /api/detection`. Includes exponential backoff. |
| `socket_client.py` | ~110 | Asynchronous Socket.IO client for non-blocking alerts (`detection_alert`, `camera_status`). |
| `config.py` | ~20 | Extracts environment variables (URLs, timeouts, keys). |
