"""Synchronous queries. The caller opens the connection and commits."""

from app.repositories.notes import create_note, list_notes
from app.repositories.tasks import create_task, list_tasks

__all__ = [
    "create_note",
    "create_task",
    "list_notes",
    "list_tasks",
]
