"""Loads Maddie's sample notes into the notes table for tests and the demo."""

import importlib.util
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

from app.repositories import create_note

BACKEND_DIR = Path(__file__).resolve().parents[3]
MADDIE_DIR = BACKEND_DIR / "Maddie" / "Week 1"


def _maddie_loader():
    spec = importlib.util.spec_from_file_location(
        "maddie_note_loader", MADDIE_DIR / "NoteReqDraft.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_sample_notes():
    notes, errors = _maddie_loader().load_folder(str(MADDIE_DIR / "notes"))
    if errors:
        raise RuntimeError(f"Some sample notes failed to load: {errors}")
    return [note.to_dict() for note in notes]


def insert_sample_notes(db, user_id):
    """Saves the notes for user_id. Returns {maddie_id: database_id}."""
    id_map = {}
    for note in load_sample_notes():
        saved = create_note(db, user_id, note["title"], note["content"], "markdown")
        id_map[note["id"]] = saved["id"]
    return id_map


def test_database_url():
    load_dotenv(BACKEND_DIR / ".env")
    url = os.getenv("TEST_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("TEST_DATABASE_URL is missing. Copy backend/.env.example to backend/.env.")
    if not (make_url(url).database or "").endswith("_test"):
        raise RuntimeError("TEST_DATABASE_URL must point at a database ending in _test.")
    return url
