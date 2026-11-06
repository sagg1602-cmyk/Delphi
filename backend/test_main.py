"""Persistence tests. Uses TEST_DATABASE_URL only and never reads DATABASE_URL."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine, make_url

from app.core.database import make_engine, upgrade_database
from app.main import create_app
from app.repositories.tasks import list_active_tasks

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


def rebuild_test_database(url: str) -> None:
    """Drop leftover Week 1 tables, then apply the Alembic migration."""
    engine = make_engine(url)
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    DROP TABLE IF EXISTS alembic_version, interests, tasks, notes, users
                    CASCADE
                    """
                )
            )
    finally:
        engine.dispose()
    upgrade_database(url)


def truncate_user_data(url: str) -> None:
    engine = make_engine(url)
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE notes, tasks, interests RESTART IDENTITY"))
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def migrated_database() -> None:
    rebuild_test_database(require_test_database_url())


@pytest.fixture(scope="module")
def test_engine(migrated_database: None) -> Iterator[Engine]:
    engine = make_engine(require_test_database_url())
    yield engine
    engine.dispose()


def test_notes_and_tasks_persist_across_restart(migrated_database: None) -> None:
    url = require_test_database_url()
    truncate_user_data(url)

    note_body = {
        "title": "Binary search trees",
        "content": "Left < parent < right.",
        "source_type": "manual",
        "source_path": "notes/binary-search.md",
    }
    task_body = {
        "title": "Finish problem set 4",
        "due_date": "2026-10-30",
        "status": "todo",
    }
    interest_body = {"name": "python"}

    first = make_engine(url)
    try:
        with TestClient(create_app(first)) as client:
            note_response = client.post("/notes", json=note_body)
            task_response = client.post("/tasks", json=task_body)
            interest_response = client.post("/interests", json=interest_body)
    finally:
        first.dispose()

    assert note_response.status_code == 201
    assert task_response.status_code == 201
    assert interest_response.status_code == 201
    created_note = note_response.json()
    created_task = task_response.json()
    created_interest = interest_response.json()
    assert created_note["user_id"] == 1
    assert created_note["source_path"] == note_body["source_path"]
    assert created_note["created_at"] == created_note["updated_at"]
    assert created_task["created_at"] == created_task["updated_at"]
    assert created_task["duration_minutes"] is None
    assert created_task["priority"] is None
    assert created_interest["active"] is True

    second = make_engine(url)
    try:
        with TestClient(create_app(second)) as client:
            notes_response = client.get("/notes")
            tasks_response = client.get("/tasks")
            interests_response = client.get("/interests")
            deleted = client.delete(f"/notes/{created_note['id']}")
            patched = client.patch(
                f"/tasks/{created_task['id']}",
                json={"status": "done"},
            )
    finally:
        second.dispose()

    assert notes_response.status_code == 200
    assert tasks_response.status_code == 200
    assert interests_response.status_code == 200
    assert notes_response.json()[0]["id"] == created_note["id"]
    assert tasks_response.json()[0]["id"] == created_task["id"]
    assert interests_response.json()[0]["name"] == "python"
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert patched.status_code == 200
    assert patched.json()["status"] == "done"
    assert patched.json()["updated_at"] != patched.json()["created_at"]

    third = make_engine(url)
    try:
        with TestClient(create_app(third)) as client:
            notes_response = client.get("/notes")
            missing = client.get(f"/notes/{created_note['id']}")
            tasks_response = client.get("/tasks")
            interests_response = client.get("/interests")
        with third.connect() as conn:
            active = list_active_tasks(conn, created_task["user_id"])
    finally:
        third.dispose()

    assert notes_response.status_code == 200
    assert notes_response.json() == []
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Note not found"
    assert tasks_response.json()[0]["status"] == "done"
    assert tasks_response.json()[0]["title"] == task_body["title"]
    assert interests_response.json()[0]["id"] == created_interest["id"]
    assert active == []


def test_second_user_sees_nothing(migrated_database: None) -> None:
    url = require_test_database_url()
    truncate_user_data(url)
    engine = make_engine(url)
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO users (external_id, name)
                    VALUES ('dev-user-2', 'dev-user-2')
                    ON CONFLICT (external_id) DO NOTHING
                    """
                )
            )
        with TestClient(create_app(engine)) as client:
            note = client.post("/notes", json={"title": "Private note", "content": "secret"})
            task = client.post("/tasks", json={"title": "Private task"})
            interest = client.post("/interests", json={"name": "python"})
            assert note.status_code == 201
            assert task.status_code == 201
            assert interest.status_code == 201
            headers = {"X-Dev-User": "dev-user-2"}
            assert client.get("/notes", headers=headers).json() == []
            assert client.get("/tasks", headers=headers).json() == []
            assert client.get("/interests", headers=headers).json() == []
            hidden = client.get(f"/notes/{note.json()['id']}", headers=headers)
            assert hidden.status_code == 404
            assert hidden.json()["detail"] == "Note not found"
            missing_user = client.get("/notes", headers={"X-Dev-User": "missing-user"})
            assert missing_user.status_code == 404
            assert missing_user.json()["detail"] == "User not found"
    finally:
        engine.dispose()


def test_patch_clears_due_date(test_engine: Engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        created = client.post(
            "/tasks",
            json={"title": "Clear the due date", "due_date": "2026-10-30"},
        )
        assert created.status_code == 201
        task_id = created.json()["id"]
        cleared = client.patch(f"/tasks/{task_id}", json={"due_date": None})
    assert cleared.status_code == 200
    assert cleared.json()["due_date"] is None
    assert cleared.json()["title"] == "Clear the due date"


def test_duplicate_interest_is_conflict(test_engine: Engine) -> None:
    with test_engine.begin() as conn:
        conn.execute(text("DELETE FROM interests WHERE name = 'duplicate-interest'"))
    with TestClient(create_app(test_engine)) as client:
        first = client.post("/interests", json={"name": "duplicate-interest"})
        second = client.post("/interests", json={"name": "duplicate-interest"})
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Interest already exists"


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
