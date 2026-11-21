"""Test database helpers. Drops tables only when the database name ends in _test."""

import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.core.database import make_engine, upgrade_database

BACKEND_DIR = Path(__file__).resolve().parents[1]


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
    """Drop leftover tables in the test database, then apply Alembic."""
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
