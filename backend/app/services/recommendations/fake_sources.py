"""Explicit fake data source for tests and demos only."""

import json
from copy import deepcopy
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).resolve().parents[4]
    / "shared"
    / "fixtures"
    / "recommendations_week2.input.json"
)


class FakeSources:
    """Provide sample data through the context builder's adapter methods."""

    def __init__(self, context):
        self.context = deepcopy(context)

    @classmethod
    def from_fixture(cls):
        context = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        return cls(context)

    def list_tasks(self, db, user_id):
        return deepcopy([
            task for task in self.context.get("tasks", [])
            if task.get("user_id") == user_id
        ])

    def list_interests(self, db, user_id):
        return deepcopy([
            interest for interest in self.context.get("interests", [])
            if interest.get("user_id") == user_id
        ])

    def retrieve_notes(self, db, user_id, tasks, interests):
        # Candidate notes only. The engine checks keyword relevance.
        return deepcopy([
            note for note in self.context.get("retrieved_notes", [])
            if note.get("user_id") == user_id
        ])

    def load_catalog(self):
        return deepcopy(self.context.get("catalog", []))