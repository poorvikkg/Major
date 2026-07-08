"""
faiss_search.py
---------------
Purpose  : Search a FAISS IndexFlatIP using a query embedding.
Inputs   : index     — live faiss.IndexFlatIP.
           id_map    — Dict[int, int] mapping FAISS row → person_id.
           query     — (D,) float32 L2-normalised embedding.
           top_k     — number of nearest neighbours to retrieve.
           threshold — minimum cosine similarity score to include a result.
Outputs  : List of dicts: [{person_id, score, rank}, ...], sorted by score desc.
Raises   : N/A — returns empty list when index is empty or no match found.

Single Responsibility: FAISS search logic ONLY.
No index mutation, no persistence, no lifecycle management lives here.
"""

import logging
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def search_index(
    index,
    id_map:    Dict[int, int],
    query:     np.ndarray,
    top_k:     int   = 3,
    threshold: float = 0.4,
) -> List[Dict]:
    """
    Run a cosine-similarity nearest-neighbour search.

    Purpose  : Find the top-k most similar persons in the FAISS index.
    Inputs   : index     — faiss.IndexFlatIP with ntotal > 0.
               id_map    — {faiss_row_idx: person_id} mapping.
               query     — (D,) float32 L2-normalised query embedding.
               top_k     — candidates to retrieve before threshold filtering.
               threshold — cosine similarity floor; results below are dropped.
    Outputs  : List[{person_id: int, score: float, rank: int}],
               sorted by score descending. Empty if no match or empty index.
    Raises   : N/A.
    """
    if index.ntotal == 0:
        logger.debug("search_index: index is empty — returning [].")
        return []

    effective_k = min(top_k, index.ntotal)
    query_vec   = _prepare_query(query)

    scores, indices = index.search(query_vec, effective_k)  # (1, k)

    results: List[Dict] = []
    for rank, (score, row_idx) in enumerate(zip(scores[0], indices[0])):
        if row_idx < 0:               # FAISS uses -1 for padding
            continue
        if float(score) < threshold:  # below similarity floor
            continue
        person_id = id_map.get(int(row_idx))
        if person_id is None:
            logger.warning("search_index: row %d not in id_map — skipping.", row_idx)
            continue
        results.append({
            "person_id": person_id,
            "score":     float(score),
            "rank":      rank,
        })

    logger.debug(
        "search_index: top_k=%d | threshold=%.2f | results=%d.",
        top_k, threshold, len(results),
    )
    return results


def _prepare_query(query: np.ndarray) -> np.ndarray:
    """
    Reshape and ensure the query is a (1, D) contiguous float32 array.

    Purpose  : Normalise query shape for FAISS .search() call.
    Inputs   : query — (D,) or (1, D) float32 array.
    Outputs  : (1, D) contiguous float32 array.
    """
    vec = query.reshape(1, -1).astype(np.float32)
    return np.ascontiguousarray(vec)
