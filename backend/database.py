"""Schema entry point. The implementation lives in app.core.database."""

from app.core.database import (
    database_url,
    get_current_user_id,
    init_schema,
    make_engine,
    main,
)

__all__ = [
    "database_url",
    "get_current_user_id",
    "init_schema",
    "make_engine",
    "main",
]

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
