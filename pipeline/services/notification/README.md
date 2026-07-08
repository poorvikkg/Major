# pipeline/services/notification

## Purpose
Dispatch detection alerts and persist matched frames.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `notifier.py` | ~160 | Dispatches alerts to HTTP, Socket.IO, and Postgres. Prevents alert flooding via a cooldown cache. |
