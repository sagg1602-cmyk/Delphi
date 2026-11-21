"""Read recommendation inputs from PostgreSQL and the catalog file.

Tests can still pass a fake adapter. The running API uses this one.
An empty user produces empty lists. This module does not invent rows.
"""

import json
from pathlib import Path

from app.repositories.interests import list_active_interests
from app.repositories.tasks import list_active_tasks
from app.services.memory.retrieval import build_task_query, retrieve_notes

CATALOG_PATH = (
    Path(__file__).resolve().parents[4] / "shared" / "fixtures" / "resources.json"
)


class LiveSources:
    """Adapter the recommendation context builder calls."""

    def list_tasks(self, db, user_id):
        return list_active_tasks(db, user_id)

    def list_interests(self, db, user_id):
        return list_active_interests(db, user_id)

    def retrieve_notes(self, db, user_id, tasks, interests):
        titles = " ".join(task.get("title") or "" for task in tasks)
        query = build_task_query(titles, interests)
        if not query:
            return []
        return [
            {
                "id": row["note_id"],
                "user_id": row["user_id"],
                "title": row["title"],
                "excerpt": row["excerpt"],
            }
            for row in retrieve_notes(db, user_id, query, limit=5)
        ]

    def load_catalog(self):
        if not CATALOG_PATH.is_file():
            raise FileNotFoundError(f"Catalog file is missing: {CATALOG_PATH}")
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Catalog file must be a list")
        return data
