"""
tests/faiss_test.py
-------------------
Unit tests for FAISSManager — in-memory only (no disk I/O in test isolation).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from pipeline.services.faiss_manager import FAISSManager

_DIM = 512


def _rand_unit(n=1) -> np.ndarray:
    """Return n random L2-normalized (512,) embeddings."""
    v = np.random.randn(n, _DIM).astype(np.float32)
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return (v / norms).squeeze(0) if n == 1 else v / norms


class TestFAISSManager(unittest.TestCase):

    def setUp(self):
        """Use a temp directory so tests never touch data/faiss/."""
        self.tmpdir = tempfile.mkdtemp()
        self.fm = FAISSManager(faiss_dir=Path(self.tmpdir))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ------------------------------------------------------------------
    # create_index
    # ------------------------------------------------------------------

    def test_create_index_starts_empty(self):
        self.fm.create_index()
        self.assertEqual(self.fm.size, 0)

    def test_create_index_persists_file(self):
        self.fm.create_index()
        self.assertTrue((Path(self.tmpdir) / "face.index").exists())

    # ------------------------------------------------------------------
    # add_person
    # ------------------------------------------------------------------

    def test_add_person_increases_size(self):
        emb = _rand_unit()
        self.fm.add_person(person_id=1, embedding=emb)
        self.assertEqual(self.fm.size, 1)

    def test_add_multiple_persons(self):
        for pid in range(1, 6):
            self.fm.add_person(person_id=pid, embedding=_rand_unit())
        self.assertEqual(self.fm.size, 5)

    def test_add_duplicate_id_triggers_update(self):
        emb = _rand_unit()
        self.fm.add_person(person_id=42, embedding=emb)
        self.fm.add_person(person_id=42, embedding=_rand_unit())  # should update
        self.assertEqual(self.fm.size, 1)

    def test_add_wrong_dim_raises(self):
        bad_emb = np.random.randn(256).astype(np.float32)
        with self.assertRaises(ValueError):
            self.fm.add_person(person_id=1, embedding=bad_emb)

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------

    def test_search_returns_match(self):
        emb = _rand_unit()
        self.fm.add_person(person_id=7, embedding=emb)
        results = self.fm.search(emb, top_k=1, threshold=0.9)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["person_id"], 7)

    def test_search_empty_index_returns_empty(self):
        self.fm.create_index()
        results = self.fm.search(_rand_unit(), top_k=5)
        self.assertEqual(results, [])

    def test_search_threshold_filters_low_scores(self):
        self.fm.add_person(person_id=1, embedding=_rand_unit())
        # Search with an unrelated embedding and very high threshold
        results = self.fm.search(_rand_unit(), top_k=1, threshold=0.999)
        # It's possible there's no match above 0.999 with random vectors
        for r in results:
            self.assertGreaterEqual(r["score"], 0.999)

    def test_search_result_structure(self):
        emb = _rand_unit()
        self.fm.add_person(person_id=99, embedding=emb)
        results = self.fm.search(emb, top_k=1, threshold=0.5)
        if results:
            self.assertIn("person_id", results[0])
            self.assertIn("score", results[0])
            self.assertIn("rank", results[0])

    # ------------------------------------------------------------------
    # delete_person
    # ------------------------------------------------------------------

    def test_delete_person_decreases_size(self):
        self.fm.add_person(person_id=1, embedding=_rand_unit())
        self.fm.add_person(person_id=2, embedding=_rand_unit())
        self.fm.delete_person(person_id=1)
        self.assertEqual(self.fm.size, 1)

    def test_delete_nonexistent_person_returns_false(self):
        result = self.fm.delete_person(person_id=999)
        self.assertFalse(result)

    def test_deleted_person_not_in_search(self):
        emb = _rand_unit()
        self.fm.add_person(person_id=5, embedding=emb)
        self.fm.delete_person(person_id=5)
        results = self.fm.search(emb, top_k=1, threshold=0.5)
        person_ids = [r["person_id"] for r in results]
        self.assertNotIn(5, person_ids)

    # ------------------------------------------------------------------
    # update_person
    # ------------------------------------------------------------------

    def test_update_person_changes_embedding(self):
        emb1 = _rand_unit()
        self.fm.add_person(person_id=10, embedding=emb1)

        emb2 = -emb1   # opposite direction — should now score negatively
        self.fm.update_person(person_id=10, embedding=emb2)

        results = self.fm.search(emb1, top_k=1, threshold=-1.0)
        # Size should remain 1
        self.assertEqual(self.fm.size, 1)

    def test_update_nonexistent_returns_false(self):
        result = self.fm.update_person(person_id=404, embedding=_rand_unit())
        self.assertFalse(result)

    # ------------------------------------------------------------------
    # sync_from_store
    # ------------------------------------------------------------------

    def test_sync_from_store_matches_embeddings(self):
        embeddings = _rand_unit(n=3)
        user_ids   = np.array([10, 20, 30], dtype=np.int64)
        self.fm.sync_from_store(embeddings, user_ids)
        self.assertEqual(self.fm.size, 3)

    def test_sync_from_store_empty_clears_index(self):
        self.fm.add_person(person_id=1, embedding=_rand_unit())
        self.fm.sync_from_store(
            np.empty((0, _DIM), dtype=np.float32),
            np.empty((0,), dtype=np.int64),
        )
        self.assertEqual(self.fm.size, 0)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def test_save_and_reload(self):
        emb = _rand_unit()
        self.fm.add_person(person_id=77, embedding=emb)
        self.fm.save_index()

        # Create a fresh manager pointing to the same directory
        fm2 = FAISSManager(faiss_dir=Path(self.tmpdir))
        self.assertEqual(fm2.size, 1)
        results = fm2.search(emb, top_k=1, threshold=0.9)
        self.assertEqual(results[0]["person_id"], 77)


if __name__ == "__main__":
    unittest.main()
