"""Request dependencies. Week 3 replaces get_current_user_id."""

from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.database import DEFAULT_EXTERNAL_ID


def get_db(request: Request) -> Iterator[Connection]:
    """One transaction for the request. The same connection is reused below."""
    with request.app.state.engine.begin() as connection:
        yield connection


def get_current_user_id(
    db: Connection = Depends(get_db),
    x_dev_user: str | None = Header(
        default=None,
        alias="X-Dev-User",
        description="Dev user external id. Defaults to dev-user-1.",
    ),
) -> int:
    """DEV ONLY. Read X-Dev-User and return that user's integer id.

    A missing or blank header selects dev-user-1. An unknown external id is 404.
    """
    external_id = (x_dev_user or "").strip() or DEFAULT_EXTERNAL_ID
    row = db.execute(
        text("SELECT id FROM users WHERE external_id = :external_id"),
        {"external_id": external_id},
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row.id
