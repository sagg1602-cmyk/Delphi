"""Task queries. The caller owns the connection and the transaction."""

from datetime import date

from sqlalchemy import text
from sqlalchemy.engine import Connection


def create_task(
    db: Connection,
    user_id: int,
    title: str,
    due_date: date | None,
    status: str,
) -> dict:
    row = (
        db.execute(
            text(
                """
                INSERT INTO tasks (user_id, title, due_date, status)
                VALUES (:user_id, :title, :due_date, :status)
                RETURNING id, user_id, title, due_date, status,
                          created_at, updated_at
                """
            ),
            {
                "user_id": user_id,
                "title": title,
                "due_date": due_date,
                "status": status,
            },
        )
        .mappings()
        .one()
    )
    return dict(row)


def list_tasks(db: Connection, user_id: int) -> list[dict]:
    rows = (
        db.execute(
            text(
                """
                SELECT id, user_id, title, due_date, status,
                       created_at, updated_at
                FROM tasks
                WHERE user_id = :user_id
                ORDER BY created_at DESC, id DESC
                """
            ),
            {"user_id": user_id},
        )
        .mappings()
        .all()
    )
    return [dict(row) for row in rows]
