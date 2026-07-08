"""
embedding_store.py
------------------
Purpose  : Read/write embeddings.npy, user_ids.npy, embedding_metadata.json.
Inputs   : Numpy arrays and JSON metadata.
Outputs  : Atomically written files.
Raises   : IOError on disk write failure.

Single Responsibility: Atomic disk I/O ONLY.
"""

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_EMBEDDING_DIM = 512


# ---------------------------------------------------------------------------
# NPY Array Store
# ---------------------------------------------------------------------------

def load_store(
    emb_file: Path,
    ids_file: Path,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load embeddings.npy and user_ids.npy from disk.
    Returns empty arrays if the files do not yet exist.
    """
    if emb_file.exists() and ids_file.exists():
        embeddings = np.load(str(emb_file), allow_pickle=False)
        user_ids   = np.load(str(ids_file),  allow_pickle=False)

        if embeddings.ndim != 2 or embeddings.shape[1] != _EMBEDDING_DIM:
            logger.warning(
                "Unexpected embeddings.npy shape %s — resetting store.",
                embeddings.shape,
            )
            return empty_store()

        return embeddings.astype(np.float32), user_ids.astype(np.int64)

    logger.debug("Embedding store is empty — returning zero-length arrays.")
    return empty_store()


def empty_store() -> Tuple[np.ndarray, np.ndarray]:
    return (
        np.empty((0, _EMBEDDING_DIM), dtype=np.float32),
        np.empty((0,),                dtype=np.int64),
    )


def save_store(
    emb_file: Path,
    ids_file: Path,
    embeddings: np.ndarray,
    user_ids: np.ndarray,
) -> None:
    """
    Atomically write embeddings.npy and user_ids.npy using temp-file + rename.
    Prevents partial writes from corrupting the store on crash.
    """
    _atomic_npy_save(emb_file, embeddings)
    _atomic_npy_save(ids_file, user_ids)
    logger.debug(
        "Store saved | shape=%s | ids=%s", embeddings.shape, user_ids.tolist()
    )


def _atomic_npy_save(target: Path, array: np.ndarray) -> None:
    tmp = target.with_suffix(".npy.tmp")
    try:
        np.save(str(tmp), array)
        shutil.move(str(tmp), str(target))
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# JSON Metadata Store
# ---------------------------------------------------------------------------

def load_metadata(meta_file: Path) -> Dict:
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Corrupt metadata file — resetting.")
    return {"persons": {}, "last_updated": None, "total_registered": 0}


def update_metadata(
    meta_file: Path,
    person_id: int,
    n_images: int,
    n_valid: int,
    failed_paths: List[str],
) -> None:
    meta = load_metadata(meta_file)
    now  = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    meta["persons"][str(person_id)] = {
        "person_id":         person_id,
        "registered_at":     now,
        "n_images_supplied": n_images,
        "n_images_valid":    n_valid,
        "n_images_failed":   len(failed_paths),
        "failed_paths":      failed_paths,
    }
    meta["last_updated"]       = now
    meta["total_registered"]   = len(meta["persons"])

    _atomic_json_save(meta_file, meta)


def remove_metadata(meta_file: Path, person_id: int) -> None:
    meta = load_metadata(meta_file)
    meta["persons"].pop(str(person_id), None)
    meta["last_updated"]     = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    meta["total_registered"] = len(meta["persons"])
    _atomic_json_save(meta_file, meta)


def _atomic_json_save(target: Path, data: Dict) -> None:
    tmp = target.with_suffix(".json.tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        shutil.move(str(tmp), str(target))
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
