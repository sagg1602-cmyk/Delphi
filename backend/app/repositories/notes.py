"""Note queries. The caller owns the connection and the transaction."""

from sqlalchemy import text
from sqlalchemy.engine import Connection

NOTE_COLUMNS = """
id, user_id, title, content, source_type, source_path, created_at, updated_at
"""


def create_note(
    db: Connection,
    user_id: int,
    title: str,
    content: str,
    source_type: str,
    source_path: str | None,
) -> dict:
    row = (
        db.execute(
            text(
                f"""
                INSERT INTO notes (user_id, title, content, source_type, source_path)
                VALUES (:user_id, :title, :content, :source_type, :source_path)
                RETURNING {NOTE_COLUMNS}
                """
            ),
            {
                "user_id": user_id,
                "title": title,
                "content": content,
                "source_type": source_type,
                "source_path": source_path,
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
                f"""
                SELECT {NOTE_COLUMNS}
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


def get_note(db: Connection, user_id: int, note_id: int) -> dict | None:
    row = (
        db.execute(
            text(
                f"""
                SELECT {NOTE_COLUMNS}
                FROM notes
                WHERE id = :note_id AND user_id = :user_id
                """
            ),
            {"note_id": note_id, "user_id": user_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        return None
    return dict(row)


def delete_note(db: Connection, user_id: int, note_id: int) -> bool:
    row = db.execute(
        text(
            """
            DELETE FROM notes
            WHERE id = :note_id AND user_id = :user_id
            RETURNING id
            """
        ),
        {"note_id": note_id, "user_id": user_id},
    ).one_or_none()
    return row is not None
