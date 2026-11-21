"""Persistence tests. Uses TEST_DATABASE_URL only and never reads DATABASE_URL."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.database import make_engine
from app.main import create_app
from app.repositories.interests import list_active_interests
from app.repositories.tasks import list_active_tasks
from tests.db_setup import require_test_database_url, truncate_user_data


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
            note_id = note.json()["id"]
            task_id = task.json()["id"]
            interest_id = interest.json()["id"]
            hidden = client.get(f"/notes/{note_id}", headers=headers)
            assert hidden.status_code == 404
            assert hidden.json()["detail"] == "Note not found"
            assert client.delete(f"/notes/{note_id}", headers=headers).status_code == 404
            task_patch = client.patch(
                f"/tasks/{task_id}",
                headers=headers,
                json={"status": "done"},
            )
            assert task_patch.status_code == 404
            interest_patch = client.patch(
                f"/interests/{interest_id}",
                headers=headers,
                json={"active": False},
            )
            assert interest_patch.status_code == 404
            assert client.get(f"/notes/{note_id}").json()["title"] == "Private note"
            tasks = client.get("/tasks").json()
            assert next(row for row in tasks if row["id"] == task_id)["status"] == "todo"
            interests = client.get("/interests").json()
            assert next(row for row in interests if row["id"] == interest_id)["active"] is True
            missing_user = client.get("/notes", headers={"X-Dev-User": "missing-user"})
            assert missing_user.status_code == 404
            assert missing_user.json()["detail"] == "User not found"
            missing_search = client.get(
                "/notes/search",
                headers={"X-Dev-User": "missing-user"},
            )
            assert missing_search.status_code == 404
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


def test_deactivated_interest_leaves_the_active_list(test_engine: Engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        created = client.post("/interests", json={"name": "deactivate-me"})
        assert created.status_code == 201
        interest_id = created.json()["id"]
        user_id = created.json()["user_id"]
        patched = client.patch(f"/interests/{interest_id}", json={"active": False})
        assert patched.status_code == 200
        assert patched.json()["active"] is False
        listed = client.get("/interests")
        assert any(row["id"] == interest_id and row["active"] is False for row in listed.json())
    with test_engine.connect() as conn:
        active = list_active_interests(conn, user_id)
    assert all(row["id"] != interest_id for row in active)


def test_recommendations_come_from_saved_rows(test_engine: Engine) -> None:
    url = require_test_database_url()
    truncate_user_data(url)
    with test_engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO users (external_id, name)
                VALUES ('dev-user-2', 'dev-user-2')
                ON CONFLICT (external_id) DO NOTHING
                """
            )
        )
    with TestClient(create_app(test_engine)) as client:
        note = client.post(
            "/notes",
            json={
                "title": "Binary search practice",
                "content": "Binary search halves a sorted list.",
            },
        )
        task = client.post(
            "/tasks",
            json={
                "title": "Practice binary search in Python",
                "due_date": "2026-11-22",
                "status": "todo",
            },
        )
        interest = client.post("/interests", json={"name": "python"})
        assert note.status_code == 201
        assert task.status_code == 201
        assert interest.status_code == 201
        task_id = task.json()["id"]
        first = client.post("/recommendations/generate")
        assert first.status_code == 200, first.text
        study = [
            card for card in first.json()["recommendations"] if card["type"] == "study"
        ]
        assert study and study[0]["action"]["target"] == task_id
        done = client.patch(f"/tasks/{task_id}", json={"status": "done"})
        assert done.status_code == 200
        second = client.post("/recommendations/generate")
        assert second.status_code == 200, second.text
        targets = [
            card["action"]["target"]
            for card in second.json()["recommendations"]
            if card["type"] == "study"
        ]
        assert task_id not in targets
        empty = client.post(
            "/recommendations/generate",
            headers={"X-Dev-User": "dev-user-2"},
        )
        assert empty.status_code == 200
        assert empty.json() == {"recommendations": []}


def test_health_ok(test_engine: Engine) -> None:
    with TestClient(create_app(test_engine)) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
