"""
embedding_backup.py
-------------------
Purpose  : Backup the embedding store before mutations.
Inputs   : Paths to embeddings.npy and user_ids.npy.
Outputs  : Copies of files in the backup directory with timestamps.
Raises   : N/A (silently skips if source files don't exist).

Single Responsibility: Disk backups ONLY.
"""

import logging
import shutil
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def backup_current_store(
    emb_file: Path,
    ids_file: Path,
    backup_dir: Path,
) -> None:
    """
    Copy the current embeddings.npy and user_ids.npy to the backup directory
    with a timestamp suffix.
    """
    ts = time.strftime("%Y%m%d_%H%M%S")
    for src in (emb_file, ids_file):
        if src.exists():
            dst = backup_dir / f"{src.stem}_{ts}{src.suffix}"
            shutil.copy2(str(src), str(dst))
            logger.debug("Backup created: %s", dst)
