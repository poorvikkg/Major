"""
embedding_manager.py
--------------------
Purpose  : Public facade for the embedding lifecycle.
Inputs   : FaceDetector, EmbeddingExtractor, and config.
Outputs  : Normalized embeddings or full stores.
Raises   : ValueError on insufficient valid images.

Single Responsibility: Orchestrate registration and store operations.
Math, disk I/O, and image processing are delegated.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from pipeline.services.detection.detector import FaceDetector
from pipeline.services.recognition.embedding_extractor import EmbeddingExtractor
from pipeline.services.recognition.similarity import normalize_embedding
from pipeline.config import get_config

from pipeline.services.embedding.embedding_store import (
    load_store,
    save_store,
    load_metadata,
    update_metadata,
    remove_metadata,
)
from pipeline.services.embedding.embedding_backup import backup_current_store
from pipeline.services.embedding.face_image_processor import embed_from_path

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Manages the on-disk embedding store for registered missing persons.
    """

    def __init__(
        self,
        detector:       FaceDetector,
        extractor:      EmbeddingExtractor,
        embeddings_dir: Optional[Path] = None,
    ) -> None:
        self._detector   = detector
        self._extractor  = extractor
        self._root       = Path(embeddings_dir) if embeddings_dir else Path(get_config().embeddings.store_dir)

        self._emb_file  = self._root / "embeddings.npy"
        self._ids_file  = self._root / "user_ids.npy"
        self._meta_file = self._root / "embedding_metadata.json"
        self._backup    = self._root / "backup"

        self._root.mkdir(parents=True, exist_ok=True)
        self._backup.mkdir(parents=True, exist_ok=True)

        logger.info("EmbeddingManager initialised | root=%s", self._root)

    def register_person(
        self,
        person_id: int,
        image_paths: List[str],
        min_valid_images: int = 1,
    ) -> np.ndarray:
        """Register (or re-register) a person from a list of image files."""
        if not image_paths:
            raise ValueError(f"No image paths supplied for person_id={person_id}.")

        logger.info("Registering person_id=%d from %d image(s).", person_id, len(image_paths))

        per_image_embeddings: List[np.ndarray] = []
        failed_paths: List[str] = []

        for path in image_paths:
            emb = embed_from_path(path, self._detector, self._extractor)
            if emb is not None:
                per_image_embeddings.append(emb)
            else:
                failed_paths.append(path)

        if failed_paths:
            logger.warning(
                "person_id=%d — %d image(s) failed embedding: %s",
                person_id, len(failed_paths), failed_paths,
            )

        if len(per_image_embeddings) < min_valid_images:
            raise ValueError(
                f"Only {len(per_image_embeddings)} valid embedding(s) produced for "
                f"person_id={person_id}; need at least {min_valid_images}."
            )

        # Average and normalize
        averaged  = np.mean(np.stack(per_image_embeddings, axis=0), axis=0)
        embedding = normalize_embedding(averaged)

        # Persist to disk
        backup_current_store(self._emb_file, self._ids_file, self._backup)
        embeddings, user_ids = load_store(self._emb_file, self._ids_file)

        if person_id in user_ids:
            idx = int(np.where(user_ids == person_id)[0][0])
            embeddings[idx] = embedding
            logger.info("Updated embedding for existing person_id=%d at row %d.", person_id, idx)
        else:
            embeddings = np.vstack([embeddings, embedding[np.newaxis, :]])
            user_ids   = np.append(user_ids, person_id)
            logger.info("Appended new embedding for person_id=%d.", person_id)

        save_store(self._emb_file, self._ids_file, embeddings, user_ids)
        update_metadata(
            self._meta_file,
            person_id=person_id,
            n_images=len(image_paths),
            n_valid=len(per_image_embeddings),
            failed_paths=failed_paths,
        )

        logger.info(
            "Registration complete for person_id=%d | store_size=%d.",
            person_id, len(user_ids),
        )
        return embedding

    def delete_person(self, person_id: int) -> bool:
        """Remove a person's embedding from the store."""
        embeddings, user_ids = load_store(self._emb_file, self._ids_file)
        mask = user_ids == person_id

        if not np.any(mask):
            logger.warning("delete_person: person_id=%d not found in store.", person_id)
            return False

        backup_current_store(self._emb_file, self._ids_file, self._backup)
        keep       = ~mask
        embeddings = embeddings[keep]
        user_ids   = user_ids[keep]
        
        save_store(self._emb_file, self._ids_file, embeddings, user_ids)
        remove_metadata(self._meta_file, person_id)

        logger.info(
            "Deleted embedding for person_id=%d | store_size=%d.", person_id, len(user_ids)
        )
        return True

    def get_all_embeddings(self) -> Tuple[np.ndarray, np.ndarray]:
        return load_store(self._emb_file, self._ids_file)

    def get_embedding(self, person_id: int) -> Optional[np.ndarray]:
        embeddings, user_ids = load_store(self._emb_file, self._ids_file)
        mask = user_ids == person_id
        if not np.any(mask):
            return None
        idx = int(np.where(mask)[0][0])
        return embeddings[idx].copy()

    def get_store_size(self) -> int:
        _, user_ids = load_store(self._emb_file, self._ids_file)
        return len(user_ids)

    def get_metadata(self) -> Dict:
        return load_metadata(self._meta_file)
