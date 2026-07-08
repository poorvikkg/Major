# pipeline/services/faiss

## Purpose
FAISS IndexFlatIP management, split into single-responsibility modules.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `faiss_index.py` | ~75 | Index lifecycle — create, load, reconstruct |
| `faiss_search.py` | ~75 | `search_index()` — cosine search, threshold filter |
| `faiss_update.py` | ~140 | `add`, `delete`, `update` — mutation with rebuild |
| `faiss_storage.py` | ~110 | Atomic disk I/O — save, load id_map, backup |
| `faiss_manager.py` | ~185 | `FAISSManager` — public facade, state, RLock |

## Why Split?

| Old file | Lines | Problem |
|----------|-------|---------|
| `faiss_manager.py` | 397 | Search + update + persistence + lifecycle all in one class |

## Key Design Decisions

- **IndexFlatIP** — exact cosine similarity on L2-normalised ArcFace embeddings; no quantisation loss.
- **Atomic writes** — `temp file → rename` prevents index corruption on crash.
- **O(1) add** — `index.add()` never rebuilds.
- **O(N) delete/update** — IndexFlatIP has no native delete; rebuild is acceptable for galleries < 100k.
- **Thread-safe** — `FAISSManager` holds an `RLock`; all public methods acquire it.

## Operation Cost Table

| Operation | Cost | Rebuild? |
|-----------|------|----------|
| `add_person()` | O(1) | ❌ No |
| `search()` | O(N·D) exact | ❌ No |
| `delete_person()` | O(N·D) | ✅ Yes |
| `update_person()` | O(N·D) | ✅ Yes |
| `sync_from_store()` | O(N·D) | ✅ Yes (startup only) |

## How It Interacts

```
EmbeddingManager  →  (N×D) embeddings, (N,) user_ids
                             │
                             ▼
                    FAISSManager.sync_from_store()    ← faiss_index.reconstruct_index()
                    FAISSManager.add_person()          ← faiss_update.add_embedding()
                    FAISSManager.delete_person()       ← faiss_update.delete_embedding()
                             │
                             ▼ (all saved via)
                    faiss_storage.save_all()          ← atomic temp→rename

FaceInference  →  query_embedding
                      │
                      ▼
             FAISSManager.search()  →  faiss_search.search_index()
                      │
                      ▼
             [{person_id, score, rank}, ...]  →  Notifier
```

## Usage

```python
from pipeline.services.faiss import FAISSManager

faiss = FAISSManager()          # loads from disk or creates fresh
faiss.add_person(42, embedding) # O(1)
results = faiss.search(query_embedding, top_k=3)
print(results)  # [{"person_id": 42, "score": 0.91, "rank": 0}]
```
