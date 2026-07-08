"""
association.py
--------------
Purpose  : Greedy bipartite matching for detection-to-track assignment.
Inputs   : (M, N) float cost matrix (lower = better match).
Outputs  : List of (row_index, col_index) matched pairs.
Raises   : N/A — returns empty list for empty input.

Single Responsibility: cost-matrix minimisation ONLY.
No IoU computation, no Kalman state, no track lifecycle lives here.

Why greedy instead of Hungarian?
  - Face count per frame is rarely > 20.
  - Greedy O(N²) is fast enough and avoids a scipy dependency.
  - Hungarian is available as a drop-in replacement if needed.
"""

from typing import List, Tuple

import numpy as np


def greedy_match(cost_matrix: np.ndarray) -> List[Tuple[int, int]]:
    """
    Find a minimum-cost bipartite matching via greedy selection.

    Each row and each column is matched at most once.  Pairs are selected
    in ascending cost order until all possible matches are exhausted.

    Purpose  : Assign detections (rows) to tracks (columns) efficiently.
    Inputs   : cost_matrix — (M, N) float array; lower = better.
    Outputs  : List of (row_idx, col_idx) pairs, sorted by cost ascending.
    Raises   : N/A.
    """
    if cost_matrix.size == 0:
        return []

    matched:    List[Tuple[int, int]] = []
    taken_rows: set = set()
    taken_cols: set = set()

    for flat_idx in np.argsort(cost_matrix.ravel()):
        r, c = divmod(int(flat_idx), cost_matrix.shape[1])
        if r not in taken_rows and c not in taken_cols:
            matched.append((r, c))
            taken_rows.add(r)
            taken_cols.add(c)
            if len(taken_rows) == cost_matrix.shape[0]:
                break  # all detections assigned

    return matched


def unmatched_indices(
    total: int,
    matched_pairs: List[Tuple[int, int]],
    axis: int,
) -> List[int]:
    """
    Return indices along one axis that have no match.

    Purpose  : Identify unmatched detections (axis=0) or tracks (axis=1).
    Inputs   : total        — length of the axis.
               matched_pairs — list from greedy_match().
               axis          — 0 for rows (detections), 1 for columns (tracks).
    Outputs  : Sorted list of unmatched integer indices.
    """
    matched_set = {pair[axis] for pair in matched_pairs}
    return [i for i in range(total) if i not in matched_set]
