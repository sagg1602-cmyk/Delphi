"""Note queries. The caller owns the connection and the transaction."""

from sqlalchemy import text
from sqlalchemy.engine import Connection


def create_note(
    db: Connection,
    user_id: int,
    title: str,
    content: str,
    source_type: str,
) -> dict:
    row = (
        db.execute(
            text(
                """
                INSERT INTO notes (user_id, title, content, source_type)
                VALUES (:user_id, :title, :content, :source_type)
                RETURNING id, user_id, title, content, source_type,
                          created_at, updated_at
                """
            ),
            {
                "user_id": user_id,
                "title": title,
                "content": content,
                "source_type": source_type,
            },
        )
        .mappings()
        .one()
    )
    return dict(row)


def list_notes(db: Connection, user_id: int) -> list[dict]:
    rows = (
        db.execute(
            text(
                """
                SELECT id, user_id, title, content, source_type,
                       created_at, updated_at
                FROM notes
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
