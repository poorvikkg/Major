"""
recognition_service.py
----------------------
High-level face recognition service for the AI pipeline.

Wraps FaceInference + EmbeddingManager + FAISSManager with business logic:
- Register a person (embedding generation + FAISS sync)
- Delete a person (embedding removal + FAISS sync)
- Search a single embedding against the index
- Provides a clean interface for callers that should not touch
  FaceInference or FAISSManager directly.
"""

import logging
from typing import Dict, List, Optional

import numpy as np

from pipeline.services.embedding_manager import EmbeddingManager
from pipeline.services.faiss_manager     import FAISSManager
from pipeline.services.inference         import FaceInference
from pipeline.database.postgres          import PostgresRepository

logger = logging.getLogger(__name__)


class RecognitionService:
    """
    Orchestrates person registration, deletion, and live recognition queries.

    Parameters
    ----------
    embedding_mgr : EmbeddingManager (manages .npy files).
    faiss_mgr     : FAISSManager (manages the FAISS index).
    inference     : FaceInference (detector + recognizer).
    db_repo       : PostgresRepository (for person metadata).
    """

    def __init__(
        self,
        embedding_mgr: EmbeddingManager,
        faiss_mgr:     FAISSManager,
        inference:     FaceInference,
        db_repo:       PostgresRepository,
    ) -> None:
        self._emb_mgr  = embedding_mgr
        self._faiss    = faiss_mgr
        self._inference = inference
        self._db        = db_repo
        logger.info("RecognitionService initialised.")

    # ------------------------------------------------------------------
    # Person registration
    # ------------------------------------------------------------------

    def register_person(
        self,
        person_id:   int,
        image_paths: List[str],
    ) -> Dict:
        """
        Register a missing person from their face images.

        Steps:
          1. Generate averaged + normalized embedding via EmbeddingManager.
          2. Add / update the person in the FAISS index.

        Parameters
        ----------
        person_id   : DB person primary key.
        image_paths : List of local image file paths.

        Returns
        -------
        {"success": bool, "person_id": int, "message": str}
        """
        try:
            embedding = self._emb_mgr.register_person(
                person_id=person_id,
                image_paths=image_paths,
            )
            # Sync to FAISS (add or update)
            if person_id in [pid for pid in self._faiss._id_map.values()]:
                self._faiss.update_person(person_id, embedding)
            else:
                self._faiss.add_person(person_id, embedding)

            logger.info("RecognitionService: person_id=%d registered.", person_id)
            return {
                "success": True,
                "person_id": person_id,
                "message": f"Person {person_id} registered successfully.",
            }
        except Exception as exc:
            logger.exception("RecognitionService: registration failed for person_id=%d.", person_id)
            return {
                "success": False,
                "person_id": person_id,
                "message": str(exc),
            }

    def delete_person(self, person_id: int) -> Dict:
        """
        Remove a person from both the embedding store and the FAISS index.

        Returns
        -------
        {"success": bool, "person_id": int, "message": str}
        """
        emb_deleted   = self._emb_mgr.delete_person(person_id)
        faiss_deleted = self._faiss.delete_person(person_id)

        success = emb_deleted or faiss_deleted
        msg = (
            f"Person {person_id} deleted." if success
            else f"Person {person_id} not found in embedding store or index."
        )
        logger.info("RecognitionService: delete person_id=%d | success=%s", person_id, success)
        return {"success": success, "person_id": person_id, "message": msg}

    def sync_index_from_store(self) -> Dict:
        """
        Fully rebuild the FAISS index from the .npy embedding store.
        Use on startup or after a restore.

        Returns
        -------
        {"success": bool, "size": int, "message": str}
        """
        try:
            embeddings, user_ids = self._emb_mgr.get_all_embeddings()
            self._faiss.sync_from_store(embeddings, user_ids)
            msg = f"FAISS index synced | {len(user_ids)} person(s)."
            logger.info("RecognitionService: %s", msg)
            return {"success": True, "size": len(user_ids), "message": msg}
        except Exception as exc:
            logger.exception("RecognitionService: sync_index_from_store failed.")
            return {"success": False, "size": 0, "message": str(exc)}

    # ------------------------------------------------------------------
    # Live recognition
    # ------------------------------------------------------------------

    def search_embedding(
        self,
        embedding: np.ndarray,
        top_k:     int   = 5,
        threshold: float = 0.45,
    ) -> List[Dict]:
        """
        Search the FAISS index with a pre-computed embedding.

        Returns
        -------
        List of {"person_id": int, "score": float, "rank": int} dicts.
        """
        return self._faiss.search(embedding, top_k=top_k, threshold=threshold)

    def get_store_info(self) -> Dict:
        """Return current embedding store and FAISS index statistics."""
        meta  = self._emb_mgr.get_metadata()
        return {
            "embedding_store_size": self._emb_mgr.get_store_size(),
            "faiss_index_size":     self._faiss.size,
            "total_registered":     meta.get("total_registered", 0),
            "last_updated":         meta.get("last_updated"),
        }
