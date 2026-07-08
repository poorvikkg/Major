"""
pipeline/services/faiss/__init__.py
Public API for the faiss sub-package.
"""

from pipeline.services.faiss.faiss_manager import FAISSManager
from pipeline.services.faiss.faiss_search  import search_index
from pipeline.services.faiss.faiss_update  import add_embedding, delete_embedding, update_embedding
from pipeline.services.faiss.faiss_storage import save_all, load_id_map, backup
from pipeline.services.faiss.faiss_index   import create_empty_index, load_index_from_disk

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
