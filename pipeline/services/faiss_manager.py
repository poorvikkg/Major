"""
pipeline/services/faiss_manager.py
-----------------------------------
Backward-compatibility shim.

The FAISS implementation has been refactored into:
    pipeline/services/faiss/

This file re-exports all public symbols so that existing imports
such as `from pipeline.services.faiss_manager import FAISSManager`
continue to work without modification.

New code should import directly from the sub-package:
    from pipeline.services.faiss import FAISSManager
"""

from pipeline.services.faiss.faiss_manager import FAISSManager   # noqa: F401
from pipeline.services.faiss.faiss_search  import search_index   # noqa: F401
from pipeline.services.faiss.faiss_update  import (              # noqa: F401
    add_embedding,
    delete_embedding,
    update_embedding,
)
from pipeline.services.faiss.faiss_storage import save_all, load_id_map, backup  # noqa: F401
from pipeline.services.faiss.faiss_index   import (              # noqa: F401
    create_empty_index,
    load_index_from_disk,
)

__all__ = [
    "FAISSManager",
    "search_index",
    "add_embedding",
    "delete_embedding",
    "update_embedding",
    "save_all",
    "load_id_map",
    "backup",
    "create_empty_index",
    "load_index_from_disk",
]
