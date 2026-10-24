"""Persistence test. Uses TEST_DATABASE_URL only and never reads DATABASE_URL."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine, make_url

from database import init_schema, make_engine
from main import create_app

BACKEND_DIR = Path(__file__).resolve().parent


def load_test_database_url() -> str:
    """Read TEST_DATABASE_URL. Never reads DATABASE_URL."""
    from_env = os.environ.get("TEST_DATABASE_URL", "").strip()
    if from_env:
        return from_env
    for name in (".env", ".env.example"):
        path = BACKEND_DIR / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("TEST_DATABASE_URL="):
                value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    raise RuntimeError(
        "TEST_DATABASE_URL is missing. Set it in the environment or backend/.env. "
        "Tests never read DATABASE_URL."
    )


def require_test_database_url() -> str:
    url = load_test_database_url()
    name = make_url(url).database or ""
    if not name.endswith("_test"):
        raise RuntimeError(
            f"Refusing to run tests against database '{name}'. "
            "The database name in TEST_DATABASE_URL must end with _test."
        )
    return url


@pytest.fixture(scope="module")
def test_engine() -> Iterator[Engine]:
    engine = make_engine(require_test_database_url())
    init_schema(engine)
    yield engine
    engine.dispose()


def test_notes_and_tasks_persist_across_restart() -> None:
    url = require_test_database_url()
    setup = make_engine(url)
    try:
        init_schema(setup)
        with setup.begin() as conn:
            # Never truncate users. The seeded dev user must stay.
            conn.execute(text("TRUNCATE notes, tasks RESTART IDENTITY"))
    finally:
        setup.dispose()

    note_body = {
        "title": "Binary search trees",
        "content": "Left < parent < right.",
        "source_type": "manual",
    }
    task_body = {
        "title": "Finish problem set 4",
        "due_date": "2026-10-30",
        "status": "todo",
    }

    first = make_engine(url)
    try:
        with TestClient(create_app(first)) as client:
            note_response = client.post("/notes", json=note_body)
            task_response = client.post("/tasks", json=task_body)
    finally:
        first.dispose()

    assert note_response.status_code == 201
    assert task_response.status_code == 201
    created_note = note_response.json()
    created_task = task_response.json()
    assert created_note["updated_at"]
    assert created_note["created_at"] == created_note["updated_at"]
    assert created_task["updated_at"]
    assert created_task["created_at"] == created_task["updated_at"]

    second = make_engine(url)
    try:
        with TestClient(create_app(second)) as client:
            notes_response = client.get("/notes")
            tasks_response = client.get("/tasks")
    finally:
        second.dispose()

    assert notes_response.status_code == 200
    assert tasks_response.status_code == 200
    notes = notes_response.json()
    tasks = tasks_response.json()
    assert len(notes) == 1
    assert len(tasks) == 1

    note = notes[0]
    task = tasks[0]
    assert note["id"] == created_note["id"]
    assert note["title"] == note_body["title"]
    assert note["user_id"] == 1
    assert note["updated_at"]
    assert task["id"] == created_task["id"]
    assert task["title"] == task_body["title"]
    assert task["user_id"] == 1
    assert task["updated_at"]


def test_empty_title_is_rejected(test_engine: Engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        response = client.post("/notes", json={"title": "   "})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("title" in item["loc"] for item in detail)


def test_health_ok(test_engine: Engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
