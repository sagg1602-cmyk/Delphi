"""Migration entry point. The implementation lives in app.core.database."""

from app.core.database import database_url, main, make_engine, upgrade_database

__all__ = [
    "database_url",
    "main",
    "make_engine",
    "upgrade_database",
]

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
