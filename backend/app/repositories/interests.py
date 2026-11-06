"""Interest queries. The caller owns the connection and the transaction."""

from sqlalchemy import text
from sqlalchemy.engine import Connection

INTEREST_COLUMNS = """
id, user_id, name, active, created_at, updated_at
"""


def create_interest(db: Connection, user_id: int, name: str) -> dict:
    row = (
        db.execute(
            text(
                f"""
                INSERT INTO interests (user_id, name)
                VALUES (:user_id, :name)
                RETURNING {INTEREST_COLUMNS}
                """
            ),
            {"user_id": user_id, "name": name},
        )
        .mappings()
        .one()
    )
    return dict(row)


def list_interests(db: Connection, user_id: int) -> list[dict]:
    return _select_interests(db, user_id, active_only=False)


def list_active_interests(db: Connection, user_id: int) -> list[dict]:
    """Interests with active = true."""
    return _select_interests(db, user_id, active_only=True)


def set_interest_active(
    db: Connection,
    user_id: int,
    interest_id: int,
    active: bool,
) -> dict | None:
    row = (
        db.execute(
            text(
                f"""
                UPDATE interests
                SET active = :active, updated_at = now()
                WHERE id = :interest_id AND user_id = :user_id
                RETURNING {INTEREST_COLUMNS}
                """
            ),
            {"active": active, "interest_id": interest_id, "user_id": user_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        return None
    return dict(row)


def _select_interests(db: Connection, user_id: int, active_only: bool) -> list[dict]:
    active_filter = "AND active = true" if active_only else ""
    rows = (
        db.execute(
            text(
                f"""
                SELECT {INTEREST_COLUMNS}
                FROM interests
                WHERE user_id = :user_id
                {active_filter}
                ORDER BY created_at DESC, id DESC
                """
            ),
            {"user_id": user_id},
        )
        .mappings()
        .all()
    )
    return [dict(row) for row in rows]
