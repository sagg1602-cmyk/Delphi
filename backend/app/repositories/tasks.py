"""Task queries. The caller owns the connection and the transaction."""

from datetime import date

from sqlalchemy import text
from sqlalchemy.engine import Connection

TASK_COLUMNS = """
id, user_id, title, due_date, status, duration_minutes, priority,
created_at, updated_at
"""

TASK_UPDATABLE = (
    "title",
    "due_date",
    "status",
    "duration_minutes",
    "priority",
)


def create_task(
    db: Connection,
    user_id: int,
    title: str,
    due_date: date | None,
    status: str,
    duration_minutes: int | None = None,
    priority: str | None = None,
) -> dict:
    row = (
        db.execute(
            text(
                f"""
                INSERT INTO tasks (
                    user_id, title, due_date, status, duration_minutes, priority
                )
                VALUES (
                    :user_id, :title, :due_date, :status, :duration_minutes, :priority
                )
                RETURNING {TASK_COLUMNS}
                """
            ),
            {
                "user_id": user_id,
                "title": title,
                "due_date": due_date,
                "status": status,
                "duration_minutes": duration_minutes,
                "priority": priority,
            },
        )
        .mappings()
        .one()
    )
    return dict(row)


def list_tasks(db: Connection, user_id: int) -> list[dict]:
    return _select_tasks(db, user_id, active_only=False)


def list_active_tasks(db: Connection, user_id: int) -> list[dict]:
    """Tasks still to do. status = 'todo'. Done tasks stay on GET /tasks."""
    return _select_tasks(db, user_id, active_only=True)


def update_task(
    db: Connection,
    user_id: int,
    task_id: int,
    changes: dict,
) -> dict | None:
    unknown = set(changes) - set(TASK_UPDATABLE)
    if unknown:
        raise ValueError(f"Cannot update {', '.join(sorted(unknown))}")
    if not changes:
        raise ValueError("No fields to update")
    assignments = [f"{column} = :{column}" for column in TASK_UPDATABLE if column in changes]
    assignments.append("updated_at = now()")
    params = {column: changes[column] for column in TASK_UPDATABLE if column in changes}
    params["user_id"] = user_id
    params["task_id"] = task_id
    row = (
        db.execute(
            text(
                f"""
                UPDATE tasks
                SET {", ".join(assignments)}
                WHERE id = :task_id AND user_id = :user_id
                RETURNING {TASK_COLUMNS}
                """
            ),
            params,
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        return None
    return dict(row)


def _select_tasks(db: Connection, user_id: int, active_only: bool) -> list[dict]:
    status_filter = "AND status = 'todo'" if active_only else ""
    rows = (
        db.execute(
            text(
                f"""
                SELECT {TASK_COLUMNS}
                FROM tasks
                WHERE user_id = :user_id
                {status_filter}
                ORDER BY created_at DESC, id DESC
                """
            ),
            {"user_id": user_id},
        )
        .mappings()
        .all()
    )
    return [dict(row) for row in rows]
