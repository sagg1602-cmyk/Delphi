"""Create the dev users plus sample tasks and interests.

Notes are not seeded. Maddie's import posts those through the API.
Run after `alembic upgrade head`. Safe to run again.
"""

from datetime import date

from sqlalchemy import text

from app.core.database import DEFAULT_EXTERNAL_ID, database_url, make_engine
from app.repositories.interests import create_interest
from app.repositories.tasks import create_task

EMPTY_DEV_USER = "dev-user-2"

SAMPLE_TASKS = (
    {
        "title": "Finish problem set 4",
        "due_date": date(2026, 10, 30),
        "status": "todo",
        "duration_minutes": 90,
        "priority": "high",
    },
    {
        "title": "Economics reading",
        "due_date": date(2026, 11, 2),
        "status": "todo",
        "duration_minutes": 45,
        "priority": "medium",
    },
)

SAMPLE_INTERESTS = ("python", "sql")


def ensure_user(db, external_id: str) -> int:
    row = db.execute(
        text("SELECT id FROM users WHERE external_id = :external_id"),
        {"external_id": external_id},
    ).one_or_none()
    if row is not None:
        return row.id
    created = db.execute(
        text(
            """
            INSERT INTO users (external_id, name)
            VALUES (:external_id, :external_id)
            RETURNING id
            """
        ),
        {"external_id": external_id},
    ).one()
    return created.id


def seed(db) -> None:
    user_id = ensure_user(db, DEFAULT_EXTERNAL_ID)
    ensure_user(db, EMPTY_DEV_USER)
    for task in SAMPLE_TASKS:
        exists = db.execute(
            text(
                """
                SELECT 1 FROM tasks
                WHERE user_id = :user_id AND title = :title
                """
            ),
            {"user_id": user_id, "title": task["title"]},
        ).first()
        if exists is None:
            create_task(db, user_id, **task)
    for name in SAMPLE_INTERESTS:
        exists = db.execute(
            text(
                """
                SELECT 1 FROM interests
                WHERE user_id = :user_id AND name = :name
                """
            ),
            {"user_id": user_id, "name": name},
        ).first()
        if exists is None:
            create_interest(db, user_id, name)


def main() -> None:
    engine = make_engine(database_url())
    try:
        with engine.begin() as db:
            seed(db)
    finally:
        engine.dispose()
    print("Seed applied. dev-user-1 has sample tasks and interests. dev-user-2 has none.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
