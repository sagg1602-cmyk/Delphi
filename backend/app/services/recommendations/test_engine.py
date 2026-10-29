"""Behavior checks for the small Week 1 prototype; standard-library unittest."""

import copy
import json
import unittest

from engine import FIXTURE_DIR, SAMPLE_CATALOG, generate_recommendations


def fixture(name="due_task"):
    return json.loads((FIXTURE_DIR / f"{name}.input.json").read_text())


class RecommendationTests(unittest.TestCase):
    def test_earliest_deadline_wins_instead_of_first_task(self):
        result = generate_recommendations(fixture())
        self.assertEqual(result[0]["action_target"], "task_calc")
        self.assertIn("due in 2 days (2026-10-30)", result[0]["reason"])

    def test_completed_task_is_not_recommended(self):
        context = fixture()
        context["tasks"][1]["completed"] = True
        result = generate_recommendations(context)
        self.assertEqual(result[0]["action_target"], "task_econ")

    def test_tasks_without_deadlines_are_omitted_in_week_one(self):
        context = fixture()
        context["tasks"] = [dict(context["tasks"][0], due_date=None)]
        self.assertEqual([r["type"] for r in generate_recommendations(context)], ["discovery"])

    def test_overdue_and_due_today_reasons_are_accurate(self):
        for due, expected in [("2026-10-27", "is overdue"), ("2026-10-28", "due today")]:
            with self.subTest(due=due):
                context = fixture()
                context["tasks"][1]["due_date"] = due
                self.assertIn(expected, generate_recommendations(context)[0]["reason"])

    def test_equal_deadlines_have_a_stable_tie_break(self):
        context = fixture()
        context["tasks"][0]["due_date"] = "2026-10-30"
        first = generate_recommendations(context)
        context["tasks"].reverse()
        self.assertEqual(first, generate_recommendations(context))

    def test_only_related_note_is_cited(self):
        result = generate_recommendations(fixture())
        self.assertEqual(result[0]["evidence_ids"], ["task_calc", "note_calc"])

    def test_notes_are_optional(self):
        context = fixture()
        del context["retrieved_notes"]
        study = generate_recommendations(context)[0]
        self.assertEqual(study["evidence_ids"], ["task_calc"])
        self.assertNotIn("note", study["reason"].lower())

    def test_foreign_user_tasks_and_notes_are_not_cited(self):
        context = fixture()
        context["tasks"].insert(0, {
            "id": "foreign_task", "user_id": "someone_else", "title": "Private task",
            "due_date": "2026-01-01", "completed": False,
        })
        context["retrieved_notes"][0]["user_id"] = "someone_else"
        study = generate_recommendations(context)[0]
        self.assertEqual(study["evidence_ids"], ["task_calc"])

    def test_changed_interest_changes_only_discovery(self):
        before = generate_recommendations(fixture())
        after = generate_recommendations(fixture("changed_interest"))
        self.assertEqual(before[0], after[0])
        self.assertEqual(before[1]["evidence_ids"], ["resource_python_tutorial"])
        self.assertEqual(after[1]["evidence_ids"], ["resource_postgresql_tutorial"])

    def test_interest_matching_ignores_case_and_outer_spaces(self):
        context = fixture()
        context["interests"] = ["  PYTHON  "]
        self.assertEqual(generate_recommendations(context)[1]["evidence_ids"],
                         ["resource_python_tutorial"])

    def test_unmatched_interest_does_not_invent_a_resource(self):
        context = fixture()
        context["interests"] = ["astronomy"]
        self.assertEqual([r["type"] for r in generate_recommendations(context)], ["study"])

    def test_empty_catalog_is_respected(self):
        self.assertEqual([r["type"] for r in generate_recommendations(fixture(), catalog=[])],
                         ["study"])

    def test_no_context_returns_empty_list(self):
        self.assertEqual(generate_recommendations(fixture("no_context")), [])

    def test_output_uses_real_input_or_catalog_evidence(self):
        context = fixture()
        known_ids = {record["id"] for record in context["tasks"] + context["retrieved_notes"]}
        known_ids.update(resource["id"] for resource in SAMPLE_CATALOG)
        for recommendation in generate_recommendations(context):
            self.assertEqual(set(recommendation),
                             {"type", "title", "reason", "evidence_ids", "action_target"})
            self.assertTrue(set(recommendation["evidence_ids"]).issubset(known_ids))
            self.assertTrue(recommendation["evidence_ids"])
            if recommendation["type"] == "discovery":
                self.assertIn(recommendation["action_target"],
                              {resource["url"] for resource in SAMPLE_CATALOG})

    def test_same_input_is_repeatable_and_is_not_mutated(self):
        context = fixture()
        original = copy.deepcopy(context)
        first = generate_recommendations(context)
        self.assertEqual(first, generate_recommendations(context))
        self.assertEqual(context, original)

    def test_invalid_date_has_an_understandable_error(self):
        for value in ("2026-02-30", "tomorrow", "20261030"):
            with self.subTest(value=value):
                context = fixture()
                context["tasks"][1]["due_date"] = value
                with self.assertRaisesRegex(ValueError, "date"):
                    generate_recommendations(context)

    def test_invalid_completion_flag_is_rejected(self):
        context = fixture()
        context["tasks"][1]["completed"] = "false"
        with self.assertRaisesRegex(ValueError, "completed"):
            generate_recommendations(context)

    def test_saved_output_fixtures_match_the_engine(self):
        for name in ("due_task", "changed_interest", "no_context"):
            with self.subTest(name=name):
                expected = json.loads((FIXTURE_DIR / f"{name}.output.json").read_text())
                self.assertEqual(generate_recommendations(fixture(name)), expected)


if __name__ == "__main__":
    unittest.main()
