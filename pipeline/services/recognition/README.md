# pipeline/services/recognition

## Purpose
Face recognition using ArcFace R100, split into single-responsibility modules.

## Files

| File | Lines | Responsibility |
|------|-------|----------------|
| `recognizer.py` | ~110 | `FaceRecognizer` — ONNX session management and raw inference. |
| `embedding_extractor.py` | ~90 | `EmbeddingExtractor` — batching, validation, and pre/post-processing. |
| `similarity.py` | ~50 | Cosine similarity math and normalization. |

## Why Split?

| Old file | Lines | Problem |
|----------|-------|---------|
| `recognizer.py` | 281 | Mixed batching logic, validation, and inference all in one class. |

## How It Interacts

```
Aligned Crops (112x112)
      │
      ▼
 EmbeddingExtractor.get_embeddings_batch()
      │
      ├──→ normalizes inputs
      ├──→ calls FaceRecognizer.run_inference()
      └──→ calls similarity.normalize_embedding()
      │
      ▼
 (N, 512) L2-normalized embeddings
```
