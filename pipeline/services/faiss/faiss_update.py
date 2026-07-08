"""
faiss_update.py
---------------
Purpose  : Add, update, and delete persons in a FAISS IndexFlatIP.
Inputs   : index    — live faiss.IndexFlatIP.
           id_map   — Dict[int, int] {faiss_row_idx → person_id}.
           person_id — int DB primary key.
           embedding — (D,) float32 L2-normalised vector.
Outputs  : Modified (index, id_map) tuple.
Raises   : ValueError — embedding dimension mismatch.
           KeyError   — person_id not found on update/delete.

Single Responsibility: index mutation ONLY.
No search, no persistence, no file I/O lives here.

FAISS IndexFlatIP has NO native delete.
Delete/update rebuild the index from scratch using only the retained rows.
Add is O(1); rebuild is O(N·D) — acceptable for gallery sizes < 100k.
"""

import logging
from typing import Dict, Tuple

import numpy as np

from pipeline.services.faiss.faiss_index import reconstruct_index

logger = logging.getLogger(__name__)


def add_embedding(
    index,
    id_map:    Dict[int, int],
    person_id: int,
    embedding: np.ndarray,
    embedding_dim: int,
) -> Tuple[object, Dict[int, int]]:
    """
    Append a new person embedding to the index.

    Purpose  : Register a new person without rebuilding the index.
    Inputs   : index         — current faiss.IndexFlatIP.
               id_map        — current {row_idx: person_id} dict.
               person_id     — DB person primary key.
               embedding     — (D,) float32 L2-normalised vector.
               embedding_dim — expected dimension D.
    Outputs  : (index, id_map) — same index object, updated id_map.
    Raises   : ValueError — if embedding.shape[0] != embedding_dim.
    """
    _validate_embedding(embedding, embedding_dim)
    new_row       = index.ntotal
    id_map        = dict(id_map)          # copy — caller retains old version
    id_map[new_row] = person_id
    index.add(np.ascontiguousarray(embedding.reshape(1, -1), dtype=np.float32))
    logger.debug("add_embedding | person_id=%d | new_row=%d.", person_id, new_row)
    return index, id_map


def delete_embedding(
    index,
    id_map:       Dict[int, int],
    person_id:    int,
    embedding_dim: int,
) -> Tuple[object, Dict[int, int]]:
    """
    Remove a person from the index by rebuilding without their row.

    Purpose  : Delete support for IndexFlatIP (which has no native delete).
    Inputs   : index         — current faiss.IndexFlatIP.
               id_map        — current {row_idx: person_id} dict.
               person_id     — DB person primary key to remove.
               embedding_dim — vector dimension D.
    Outputs  : (new_index, new_id_map) after rebuild.
    Raises   : KeyError — person_id not found in id_map.
    """
    rows_to_keep = [row for row, pid in id_map.items() if pid != person_id]
    if len(rows_to_keep) == len(id_map):
        raise KeyError(f"person_id={person_id} not found in FAISS id_map.")

    kept_embeddings = _extract_rows(index, rows_to_keep, embedding_dim)
    new_index       = reconstruct_index(kept_embeddings, embedding_dim)
    new_id_map      = _rebuild_id_map(id_map, rows_to_keep)

    logger.info(
        "delete_embedding | person_id=%d | old_size=%d | new_size=%d.",
        person_id, index.ntotal, new_index.ntotal,
    )
    return new_index, new_id_map


def update_embedding(
    index,
    id_map:        Dict[int, int],
    person_id:     int,
    new_embedding: np.ndarray,
    embedding_dim: int,
) -> Tuple[object, Dict[int, int]]:
    """
    Replace a person's embedding by rebuilding the index.

    Purpose  : Update without leaving a stale row in the index.
    Inputs   : index         — current faiss.IndexFlatIP.
               id_map        — current {row_idx: person_id} dict.
               person_id     — DB person primary key to update.
               new_embedding — (D,) float32 replacement embedding.
               embedding_dim — vector dimension D.
    Outputs  : (new_index, new_id_map) after rebuild.
    Raises   : KeyError   — person_id not found.
               ValueError — embedding dimension mismatch.
    """
    _validate_embedding(new_embedding, embedding_dim)
    new_index, new_id_map = delete_embedding(index, id_map, person_id, embedding_dim)
    new_index, new_id_map = add_embedding(
        new_index, new_id_map, person_id, new_embedding, embedding_dim
    )
    logger.info("update_embedding | person_id=%d.", person_id)
    return new_index, new_id_map


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_embedding(embedding: np.ndarray, expected_dim: int) -> None:
    flat = embedding.ravel()
    if flat.shape[0] != expected_dim:
        raise ValueError(
            f"Embedding dimension mismatch: expected {expected_dim}, got {flat.shape[0]}."
        )


def _extract_rows(index, row_indices: list, embedding_dim: int) -> np.ndarray:
    """Reconstruct embedding vectors for the given row indices."""
    if not row_indices:
        return np.empty((0, embedding_dim), dtype=np.float32)
    matrix = np.empty((len(row_indices), embedding_dim), dtype=np.float32)
    for new_pos, old_row in enumerate(row_indices):
        index.reconstruct(old_row, matrix[new_pos])
    return matrix


def _rebuild_id_map(
    old_id_map:   Dict[int, int],
    rows_to_keep: list,
) -> Dict[int, int]:
    """Compact id_map so row indices are contiguous after deletion."""
    return {new_pos: old_id_map[old_row]
            for new_pos, old_row in enumerate(rows_to_keep)}
