"""
faiss_manager.py
----------------
Purpose  : Public facade for FAISS operations.
           Composes faiss_index, faiss_search, faiss_update, faiss_storage
           into a single thread-safe interface.
Inputs   : Config-driven (reads pipeline.config.FAISSConfig).
Outputs  : Search results, success booleans, index stats.
Raises   : See individual sub-modules.

Single Responsibility: state ownership + thread safety + delegation ONLY.
All algorithm logic lives in the four sub-modules.
"""

import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from pipeline.config            import get_config
from pipeline.services.faiss.faiss_index   import (
    create_empty_index, load_index_from_disk, reconstruct_index
)
from pipeline.services.faiss.faiss_search  import search_index
from pipeline.services.faiss.faiss_update  import (
    add_embedding, delete_embedding, update_embedding
)
from pipeline.services.faiss.faiss_storage import save_all, load_id_map, backup

logger = logging.getLogger(__name__)


class FAISSManager:
    """
    Thread-safe facade for the FAISS face index.

    All public methods acquire an RLock — safe for concurrent stream access.
    The index file is loaded from disk automatically on construction if it
    exists, otherwise an empty index is created.

    Parameters
    ----------
    faiss_dir     : Override the directory from config (useful in tests).
    embedding_dim : Override the dimension from config (useful in tests).
    """

    def __init__(
        self,
        faiss_dir:     Optional[Path] = None,
        embedding_dim: Optional[int]  = None,
    ) -> None:
        cfg              = get_config().faiss
        self._store_dir  = Path(faiss_dir) if faiss_dir else Path(cfg.index_dir)
        self._dim        = embedding_dim or cfg.embedding_dim
        self._threshold  = cfg.search_threshold
        self._lock       = threading.RLock()
        self._id_map:    Dict[int, int] = {}
        self._index      = self._load_or_create()
        logger.info(
            "FAISSManager ready | dir=%s | dim=%d | ntotal=%d.",
            self._store_dir, self._dim, self._index.ntotal,
        )

    # ------------------------------------------------------------------
    # Public API — reads
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: np.ndarray,
        top_k:           int           = 3,
        threshold:       Optional[float] = None,
    ) -> List[Dict]:
        """
        Cosine-similarity nearest-neighbour search.

        Purpose  : Find the best-matching persons for a query face embedding.
        Inputs   : query_embedding — (D,) float32 L2-normalised vector.
                   top_k           — max results to return.
                   threshold       — override config search_threshold.
        Outputs  : List[{person_id, score, rank}] sorted by score desc.
        """
        with self._lock:
            return search_index(
                self._index, self._id_map, query_embedding,
                top_k=top_k,
                threshold=threshold if threshold is not None else self._threshold,
            )

    @property
    def size(self) -> int:
        """Number of embeddings currently in the index."""
        with self._lock:
            return self._index.ntotal

    # ------------------------------------------------------------------
    # Public API — writes
    # ------------------------------------------------------------------

    def add_person(self, person_id: int, embedding: np.ndarray) -> None:
        """
        Add or update a person. Calls update if already present.

        Purpose  : Register a new person or refresh an existing embedding.
        Inputs   : person_id — DB person primary key.
                   embedding — (D,) float32 L2-normalised vector.
        """
        with self._lock:
            if person_id in self._id_map.values():
                self._index, self._id_map = update_embedding(
                    self._index, self._id_map, person_id, embedding, self._dim
                )
            else:
                self._index, self._id_map = add_embedding(
                    self._index, self._id_map, person_id, embedding, self._dim
                )
            save_all(self._index, self._id_map, self._store_dir)

    def delete_person(self, person_id: int) -> bool:
        """
        Remove a person from the index.

        Purpose  : De-register a person who is no longer monitored.
        Inputs   : person_id — DB person primary key.
        Outputs  : True if deleted, False if not found.
        """
        with self._lock:
            if person_id not in self._id_map.values():
                return False
            backup(self._store_dir)
            self._index, self._id_map = delete_embedding(
                self._index, self._id_map, person_id, self._dim
            )
            save_all(self._index, self._id_map, self._store_dir)
            return True

    def update_person(self, person_id: int, embedding: np.ndarray) -> bool:
        """
        Replace a person's embedding.

        Purpose  : Re-register a person after new images are added.
        Inputs   : person_id — DB person primary key.
                   embedding — (D,) float32 replacement vector.
        Outputs  : True if updated, False if not found.
        """
        with self._lock:
            if person_id not in self._id_map.values():
                return False
            self._index, self._id_map = update_embedding(
                self._index, self._id_map, person_id, embedding, self._dim
            )
            save_all(self._index, self._id_map, self._store_dir)
            return True

    def sync_from_store(
        self,
        embeddings: np.ndarray,
        user_ids:   np.ndarray,
    ) -> None:
        """
        Fully rebuild the index from an embedding matrix.

        Purpose  : Startup sync or post-restore rebuild.
        Inputs   : embeddings — (N, D) float32 L2-normalised.
                   user_ids   — (N,) int64 person IDs aligned with rows.
        """
        with self._lock:
            self._index  = reconstruct_index(embeddings, self._dim)
            self._id_map = {i: int(uid) for i, uid in enumerate(user_ids)}
            save_all(self._index, self._id_map, self._store_dir)
        logger.info("FAISS index synced | ntotal=%d.", self._index.ntotal)

    def save_index(self) -> None:
        """Manually persist the current index state to disk."""
        with self._lock:
            save_all(self._index, self._id_map, self._store_dir)

    def create_index(self) -> None:
        """Create and persist a fresh empty index (replaces existing)."""
        with self._lock:
            self._index  = create_empty_index(self._dim)
            self._id_map = {}
            save_all(self._index, self._id_map, self._store_dir)
        logger.info("Fresh FAISS index created at %s.", self._store_dir)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_or_create(self):
        """Load existing index from disk, or create empty one if absent."""
        index_path = self._store_dir / "face.index"
        try:
            idx = load_index_from_disk(index_path)
            self._id_map = load_id_map(self._store_dir)
            return idx
        except FileNotFoundError:
            logger.info("No existing FAISS index — creating fresh one.")
            self._store_dir.mkdir(parents=True, exist_ok=True)
            idx = create_empty_index(self._dim)
            save_all(idx, {}, self._store_dir)
            return idx
