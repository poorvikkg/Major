"""
faiss_index.py
--------------
Purpose  : Create and load a FAISS IndexFlatIP instance.
Inputs   : embedding_dim — vector dimension (typically 512).
           index_path    — path to a saved .index file on disk.
Outputs  : faiss.IndexFlatIP object.
Raises   : FileNotFoundError — index file not found on load.
           RuntimeError      — faiss import failed.

Single Responsibility: index creation and loading ONLY.
No search, no update, no persistence logic lives here.

Why IndexFlatIP?
  ArcFace embeddings are L2-normalised, so inner product == cosine
  similarity — exact, no quantisation loss, no approximation.
"""

import logging
from pathlib import Path

import faiss

logger = logging.getLogger(__name__)


def create_empty_index(embedding_dim: int) -> faiss.IndexFlatIP:
    """
    Create a new, empty IndexFlatIP.

    Purpose  : Initialise a fresh cosine-similarity index.
    Inputs   : embedding_dim — dimension of each embedding vector.
    Outputs  : Empty faiss.IndexFlatIP with ntotal == 0.
    Raises   : N/A.
    """
    index = faiss.IndexFlatIP(embedding_dim)
    logger.debug("Created empty IndexFlatIP | dim=%d.", embedding_dim)
    return index


def load_index_from_disk(index_path: Path) -> faiss.IndexFlatIP:
    """
    Load a previously saved FAISS index from disk.

    Purpose  : Restore a persisted index on startup.
    Inputs   : index_path — absolute path to the .index file.
    Outputs  : Loaded faiss.IndexFlatIP.
    Raises   : FileNotFoundError — file does not exist.
               RuntimeError      — file is corrupt or incompatible.
    """
    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at: {index_path}. "
            "Call FAISSManager.create_index() to initialise a new one."
        )
    try:
        index = faiss.read_index(str(index_path))
        logger.info("FAISS index loaded | path=%s | ntotal=%d.", index_path, index.ntotal)
        return index
    except Exception as exc:
        raise RuntimeError(f"Failed to load FAISS index from {index_path}: {exc}") from exc


def reconstruct_index(
    embeddings: "numpy.ndarray",  # (N, D) float32, L2-normalised
    embedding_dim: int,
) -> faiss.IndexFlatIP:
    """
    Build a fresh IndexFlatIP from a numpy embedding matrix.

    Purpose  : Rebuild the entire index after a delete/update operation.
    Inputs   : embeddings    — (N, D) float32 L2-normalised embedding matrix.
               embedding_dim — D, the vector dimension.
    Outputs  : faiss.IndexFlatIP with ntotal == N.
    Raises   : N/A.
    """
    import numpy as np  # local import — avoids top-level numpy dep in this module

    index = create_empty_index(embedding_dim)
    if embeddings.shape[0] > 0:
        vectors = np.ascontiguousarray(embeddings, dtype=np.float32)
        index.add(vectors)
    logger.debug("Reconstructed index | ntotal=%d.", index.ntotal)
    return index
