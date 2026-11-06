"""Synchronous queries. The caller opens the connection and commits.

Schema: see SCHEMA.md in this directory.
"""

from app.repositories.interests import (
    create_interest,
    list_active_interests,
    list_interests,
    set_interest_active,
)
from app.repositories.notes import create_note, delete_note, get_note, list_notes
from app.repositories.tasks import (
    create_task,
    list_active_tasks,
    list_tasks,
    update_task,
)

__all__ = [
    "create_interest",
    "create_note",
    "create_task",
    "delete_note",
    "get_note",
    "list_active_interests",
    "list_active_tasks",
    "list_interests",
    "list_notes",
    "list_tasks",
    "set_interest_active",
    "update_task",
]
