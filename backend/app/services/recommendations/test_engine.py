"""Week 2 scenario and evidence tests. No database required."""

import json
import unittest
from copy import deepcopy
from pathlib import Path

from backend.app.services.recommendations.engine import (
    generate_recommendations,
    validate_evidence,
)

FIXTURES = Path(__file__).resolve().parents[4] / "shared" / "fixtures"


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.context = json.loads(
            (FIXTURES / "recommendations_week2.input.json").read_text()
        )

    def generate(self):
        return generate_recommendations(self.context)

    def test_due_task_produces_study_and_discovery(self):
        result = self.generate()
        self.assertEqual(
            [item["type"] for item in result],
            ["study", "discovery"],
        )
        self.assertEqual(result[0]["action"]["target"], "task_calc")

    def test_changed_interest_changes_discovery(self):
        self.context["interests"][0]["name"] = "SQL"
        self.context["catalog"].append({
            "id": "resource_sql",
            "title": "PostgreSQL Tutorial",
            "tags": ["sql"],
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
        })
        discovery = self.generate()[1]
        self.assertEqual(discovery["id"], "discovery-resource_sql")

    def test_empty_user_gets_no_recommendations(self):
        self.context["tasks"] = []
        self.context["interests"] = []
        self.context["retrieved_notes"] = []
        self.assertEqual(self.generate(), [])

    def test_completed_task_is_excluded(self):
        self.context["tasks"][0]["status"] = "done"
        self.assertEqual(
            [item["type"] for item in self.generate()], ["discovery"]
        )

    def test_cancelled_task_is_excluded(self):
        self.context["tasks"][0]["status"] = "cancelled"
        self.assertEqual(
            [item["type"] for item in self.generate()], ["discovery"]
        )

    def test_deactivated_interest_is_excluded(self):
        self.context["interests"][0]["active"] = False
        self.assertEqual(
            [item["type"] for item in self.generate()], ["study"]
        )

    def test_no_notes_still_produces_study(self):
        self.context["retrieved_notes"] = []
        study = self.generate()[0]
        self.assertEqual(study["type"], "study")
        self.assertEqual(
            [item["type"] for item in study["evidence"]], ["task"]
        )

    def test_no_tasks_produces_discovery_only(self):
        self.context["tasks"] = []
        self.assertEqual(
            [item["type"] for item in self.generate()], ["discovery"]
        )

    def test_unmatched_resource_is_excluded(self):
        self.context["catalog"][0]["tags"] = ["biology"]
        self.assertEqual(
            [item["type"] for item in self.generate()], ["study"]
        )

    def test_evidence_ids_are_present_in_input(self):
        allowed = {
            (kind, type(record["id"]), record["id"])
            for kind, field in [
                ("task", "tasks"),
                ("note", "retrieved_notes"),
                ("interest", "interests"),
                ("resource", "catalog"),
            ]
            for record in self.context[field]
        }
        for recommendation in self.generate():
            for item in recommendation["evidence"]:
                self.assertIn(
                    (item["type"], type(item["id"]), item["id"]),
                    allowed,
                )

    def test_invented_evidence_is_rejected(self):
        result = self.generate()
        result[0]["evidence"][0]["id"] = "invented"
        with self.assertRaises(ValueError):
            validate_evidence(result, self.context)

    def test_changed_resource_url_is_rejected(self):
        result = self.generate()
        result[1]["action"]["target"] = "https://example.com/invented"
        with self.assertRaises(ValueError):
            validate_evidence(result, self.context)

    def test_other_users_data_is_excluded(self):
        for field in ("tasks", "interests", "retrieved_notes"):
            for record in self.context[field]:
                record["user_id"] = 999
        self.assertEqual(self.generate(), [])

    def test_numeric_database_ids_are_supported(self):
        self.context["tasks"][0]["id"] = 12
        result = self.generate()
        self.assertEqual(result[0]["action"]["target"], 12)
        self.assertEqual(result[0]["evidence"][0]["id"], 12)

    def test_generation_does_not_modify_input(self):
        original = deepcopy(self.context)
        first = self.generate()
        self.assertEqual(self.context, original)
        self.assertEqual(first, self.generate())

    def test_output_matches_shared_fixture(self):
        expected = json.loads(
            (FIXTURES / "recommendations_week2.output.json").read_text()
        )
        self.assertEqual(
            {"recommendations": self.generate()}, expected
        )


if __name__ == "__main__":
    unittest.main()