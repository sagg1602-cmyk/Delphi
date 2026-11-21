"""Loads the fictional notes in backend/test_data into the notes table."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.repositories import create_note
from app.services.imports.markdown_notes import load_folder

BACKEND_DIR = Path(__file__).resolve().parents[3]
NOTES_DIR = BACKEND_DIR / "test_data" / "notes"


def load_sample_notes():
    notes, errors = load_folder(NOTES_DIR)
    if errors:
        raise RuntimeError(f"Some sample notes failed to load: {errors}")
    return [note.to_dict() for note in notes]


def ensure_user(db, user_id: int, external_id: str, name: str) -> None:
    """Insert a user id used by retrieval checks. Existing ids are left alone."""
    db.execute(
        text(
            """
            INSERT INTO users (id, external_id, name)
            VALUES (:id, :external_id, :name)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"id": user_id, "external_id": external_id, "name": name},
    )


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
