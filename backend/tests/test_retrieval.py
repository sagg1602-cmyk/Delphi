"""Week 1 retrieval tests. Run from backend/: python -m unittest discover tests -v"""

import unittest

from app.services.memory.retrieval import retrieve_notes

USER = 1


class TestRetrieveNotes(unittest.TestCase):

    def test_query_1_biology(self):
        results = retrieve_notes(USER, "calvin cycle")
        self.assertEqual(results[0]["note_id"], 1)

    def test_query_2_math(self):
        results = retrieve_notes(USER, "eigenvalues of a matrix")
        self.assertEqual(results[0]["note_id"], 2)

    def test_query_3_paper(self):
        results = retrieve_notes(USER, "french revolution paper")
        self.assertEqual(results[0]["note_id"], 3)

    def test_results_have_required_fields(self):
        result = retrieve_notes(USER, "photosynthesis")[0]
        for field in ["note_id", "title", "excerpt", "score", "source_type"]:
            self.assertIn(field, result)
        self.assertTrue(0 < result["score"] <= 1)

    def test_never_returns_other_users_notes(self):
        results = retrieve_notes(USER, "photosynthesis calvin cycle")
        ids = [r["note_id"] for r in results]
        self.assertNotIn(6, ids)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(retrieve_notes(USER, "quantum physics"), [])

    def test_empty_query_returns_empty_list(self):
        self.assertEqual(retrieve_notes(USER, "   "), [])

    def test_limit(self):
        results = retrieve_notes(USER, "notes study cycle paper matrix", limit=2)
        self.assertLessEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
