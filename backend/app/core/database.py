"""Engine and migrations.

There is no connection at import time. Callers pass a URL into make_engine(),
so tests can open delphi_test without ever reading DATABASE_URL.
The dev-user lookup lives in app.api.deps.get_current_user_id.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Header value used when X-Dev-User is missing. Week 3 replaces the lookup.
DEFAULT_EXTERNAL_ID = "dev-user-1"

# This file lives in backend/app/core/. .env and alembic.ini stay in backend/.
BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BACKEND_DIR / ".env"
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


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


def upgrade_database(url: str | None = None) -> None:
    """Apply Alembic migrations. Pass a URL to avoid reading DATABASE_URL."""
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", url or database_url())
    command.upgrade(cfg, "head")


def main() -> None:
    upgrade_database()
    print("Migrations applied.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
