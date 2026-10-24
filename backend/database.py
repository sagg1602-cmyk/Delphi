"""Engine, schema setup, and the dev-only user dependency.

There is no connection at import time. Callers pass a URL into make_engine(),
so tests can open delphi_test without ever reading DATABASE_URL.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# DEV ONLY, replace with real auth in a later week.
DEV_USER_ID = 1

BACKEND_DIR = Path(__file__).resolve().parent
ENV_PATH = BACKEND_DIR / ".env"
SCHEMA_PATH = BACKEND_DIR / "schema.sql"


def database_url() -> str:
    """Read DATABASE_URL from backend/.env or the environment."""
    load_dotenv(ENV_PATH)
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is missing. Copy backend/.env.example to backend/.env "
            "and set DATABASE_URL before starting the API."
        )
    return url


def make_engine(url: str) -> Engine:
    """Build a synchronous engine for any database URL."""
    return create_engine(url, pool_pre_ping=True)


def _sql_statements(sql: str) -> list[str]:
    """Split a SQL script on semicolons, keeping quoted text intact."""
    statements: list[str] = []
    current: list[str] = []
    in_string = False
    i = 0
    while i < len(sql):
        char = sql[i]
        if char == "'":
            if in_string and i + 1 < len(sql) and sql[i + 1] == "'":
                current.append("''")
                i += 2
                continue
            in_string = not in_string
            current.append(char)
        elif char == ";" and not in_string:
            statement = "".join(current).strip()
            if _has_sql(statement):
                statements.append(statement)
            current = []
        else:
            current.append(char)
        i += 1
    tail = "".join(current).strip()
    if _has_sql(tail):
        statements.append(tail)
    return statements


def _has_sql(statement: str) -> bool:
    lines = [line.split("--", 1)[0] for line in statement.splitlines()]
    return bool("".join(lines).strip())


def init_schema(engine: Engine) -> None:
    """Apply schema.sql in one transaction. Safe to run more than once."""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for statement in _sql_statements(sql):
            conn.execute(text(statement))


def get_current_user_id() -> int:
    """DEV ONLY. Every request acts as the seeded development user."""
    return DEV_USER_ID


def main() -> None:
    engine = make_engine(database_url())
    try:
        init_schema(engine)
    finally:
        engine.dispose()
    print("Schema applied.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
