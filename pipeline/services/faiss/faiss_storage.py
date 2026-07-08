"""
faiss_storage.py
----------------
Purpose  : Persist and restore the FAISS index + id_map + metadata to disk.
Inputs   : faiss.IndexFlatIP, Dict id_map, Path directory.
Outputs  : Files: face.index, id_map.pkl, metadata.json (+ backups).
Raises   : OSError — disk write failure.
           FileNotFoundError — files missing on load.

Single Responsibility: disk I/O ONLY.
No index construction, no search, no update logic lives here.

All writes use atomic temp-file → rename to prevent corruption on crash.
"""

import json
import logging
import pickle
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import faiss
import numpy as np

logger = logging.getLogger(__name__)

_INDEX_FILE    = "face.index"
_ID_MAP_FILE   = "id_map.pkl"
_METADATA_FILE = "metadata.json"
_BACKUP_DIR    = "backup"


def save_all(
    index:    "faiss.IndexFlatIP",
    id_map:   Dict[int, int],
    store_dir: Path,
) -> None:
    """
    Atomically persist the index, id_map, and metadata to disk.

    Purpose  : Durable, crash-safe write of all FAISS state.
    Inputs   : index     — current faiss.IndexFlatIP.
               id_map    — current {row_idx: person_id} dict.
               store_dir — target directory (created if absent).
    Outputs  : Writes face.index, id_map.pkl, metadata.json.
    Raises   : OSError on write failure.
    """
    store_dir.mkdir(parents=True, exist_ok=True)
    _write_index(index,  store_dir / _INDEX_FILE)
    _write_id_map(id_map, store_dir / _ID_MAP_FILE)
    _write_metadata(
        metadata={
            "ntotal":         index.ntotal,
            "unique_persons": len(set(id_map.values())),
            "saved_at":       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        path=store_dir / _METADATA_FILE,
    )
    logger.info("FAISS state saved | dir=%s | ntotal=%d.", store_dir, index.ntotal)


def load_id_map(store_dir: Path) -> Dict[int, int]:
    """
    Load the id_map pickle from disk.

    Purpose  : Restore {row_idx: person_id} after a process restart.
    Inputs   : store_dir — directory containing id_map.pkl.
    Outputs  : Dict[int, int].
    Raises   : FileNotFoundError — id_map.pkl absent.
    """
    path = store_dir / _ID_MAP_FILE
    if not path.exists():
        raise FileNotFoundError(f"id_map.pkl not found at: {path}")
    with open(path, "rb") as fh:
        id_map = pickle.load(fh)
    logger.debug("id_map loaded | entries=%d.", len(id_map))
    return id_map


def backup(store_dir: Path) -> Optional[Path]:
    """
    Copy current index + id_map + metadata into a timestamped backup folder.

    Purpose  : Create a restore point before a destructive operation.
    Inputs   : store_dir — directory with current state.
    Outputs  : Path to backup directory, or None if nothing to back up.
    """
    index_path = store_dir / _INDEX_FILE
    if not index_path.exists():
        return None

    ts         = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = store_dir / _BACKUP_DIR / ts
    backup_dir.mkdir(parents=True, exist_ok=True)

    for fname in (_INDEX_FILE, _ID_MAP_FILE, _METADATA_FILE):
        src = store_dir / fname
        if src.exists():
            shutil.copy2(str(src), str(backup_dir / fname))

    logger.info("FAISS backup created | dir=%s.", backup_dir)
    return backup_dir


# ---------------------------------------------------------------------------
# Private atomic write helpers
# ---------------------------------------------------------------------------

def _write_index(index: "faiss.IndexFlatIP", dest: Path) -> None:
    """Atomically write a FAISS index file."""
    with tempfile.NamedTemporaryFile(
        dir=dest.parent, suffix=".tmp", delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)
    faiss.write_index(index, str(tmp_path))
    shutil.move(str(tmp_path), str(dest))


def _write_id_map(id_map: Dict, dest: Path) -> None:
    """Atomically pickle the id_map."""
    with tempfile.NamedTemporaryFile(
        dir=dest.parent, suffix=".tmp", delete=False, mode="wb"
    ) as tmp:
        pickle.dump(id_map, tmp)
        tmp_path = Path(tmp.name)
    shutil.move(str(tmp_path), str(dest))


def _write_metadata(metadata: Dict, dest: Path) -> None:
    """Atomically write metadata JSON."""
    with tempfile.NamedTemporaryFile(
        dir=dest.parent, suffix=".tmp", delete=False, mode="w", encoding="utf-8"
    ) as tmp:
        json.dump(metadata, tmp, indent=2)
        tmp_path = Path(tmp.name)
    shutil.move(str(tmp_path), str(dest))
