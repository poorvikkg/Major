# pipeline/database/postgres

## Purpose
PostgreSQL Data Access Layer (Repository Pattern).

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `postgres.py` | ~25 | Facade combining all specialized repositories into a single `PostgresRepository`. |
| `base_repo.py` | ~40 | Connection context-manager and JSON serialization helpers. |
| `missing_persons_repo.py` | ~50 | Queries for missing persons (all, by id, paginated). |
| `cameras_repo.py` | ~40 | Queries for camera configurations and states. |
| `detections_repo.py` | ~70 | Read/write queries for the `detection_logs` table. |
