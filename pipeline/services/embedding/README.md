# pipeline/services/embedding

## Purpose
Lifecycle management for the missing person embedding store (`data/embeddings/`), split into single-responsibility modules.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `embedding_manager.py` | ~160 | `EmbeddingManager` — facade for registration and deletions. |
| `embedding_store.py` | ~120 | Atomic disk I/O for `embeddings.npy`, `user_ids.npy`, and metadata. |
| `embedding_backup.py` | ~30 | Backups before mutations. |
| `face_image_processor.py` | ~50 | Orchestrates the detect → align → embed pipeline for a single static image. |

## Why Split?

| Old file | Lines | Problem |
|----------|-------|---------|
| `embedding_manager.py` | 427 | Mixed disk I/O, backup logic, image processing, and orchestration in one "God Class". |

## How It Interacts

```
EmbeddingManager.register_person()
      │
      ├──→ calls face_image_processor.embed_from_path()
      │       ├──→ Detector
      │       └──→ EmbeddingExtractor
      │
      ├──→ averages and normalizes embeddings
      │
      ├──→ calls embedding_backup.backup_current_store()
      │
      └──→ calls embedding_store.save_store() + update_metadata()
```
