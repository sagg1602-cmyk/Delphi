"""Create the dev users plus sample tasks and interests.

The tasks match the fictional student in docs/demo-student.md. Due dates are
counted from the day this seed runs. Notes are not seeded. Post those with
`python -m app.services.imports.load_notes` while the API is running. Run this
after `alembic upgrade head`. Running it again skips a title or interest name
that is already stored and does not move an existing due date.
"""

from datetime import date, timedelta

from sqlalchemy import text

from app.core.database import DEFAULT_EXTERNAL_ID, database_url, make_engine
from app.repositories.interests import create_interest
from app.repositories.tasks import create_task

EMPTY_DEV_USER = "dev-user-2"

# "data-science" matches the catalog tag. The recommendation engine compares
# the whole interest name with a tag, so "Data science" would not match.
SAMPLE_INTERESTS = ("Python", "data-science")


def sample_tasks(today: date | None = None) -> tuple[dict, ...]:
    """Tasks for dev-user-1. Dates are relative to today."""
    current = today or date.today()
    return (
        {
            "title": "Practice binary search in Python",
            "due_date": current + timedelta(days=2),
            "status": "todo",
            "duration_minutes": 25,
            "priority": "high",
        },
        {
            "title": "Review linear regression residuals",
            "due_date": current + timedelta(days=5),
            "status": "todo",
            "duration_minutes": None,
            "priority": None,
        },
    )


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
    for task in sample_tasks():
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
    print(
        "Seed applied. dev-user-1 has sample tasks and interests. "
        "dev-user-2 has none. Notes are not seeded."
    )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
