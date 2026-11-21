"""Delphi API: health, notes, tasks, interests, and note search for the dev user."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from app.api.health import router as health_router
from app.api.interests import router as interests_router
from app.api.memory import router as memory_router
from app.api.notes import router as notes_router
from app.api.recommendations import router as recommendations_router
from app.api.tasks import router as tasks_router
from app.core.database import database_url, make_engine
from app.services.recommendations.live_sources import LiveSources


def create_app(engine: Engine | None = None) -> FastAPI:
    """Build the API. Pass an engine to point tests at delphi_test.

    Tables come from Alembic. Starting the API does not migrate.
    Recommendations are generated from the database and the catalog file.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app_engine = engine
        owns_engine = app_engine is None
        if app_engine is None:
            app_engine = make_engine(database_url())
        app.state.engine = app_engine
        try:
            yield
        finally:
            if owns_engine:
                app_engine.dispose()

    app = FastAPI(title="Delphi API (dev only)", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.exception_handler(OperationalError)
    def database_unavailable(request: Request, exc: OperationalError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "Database unavailable"},
        )

    app.state.recommendation_sources = LiveSources()
    app.include_router(health_router)
    app.include_router(memory_router)  # before notes, so /notes/search isn't read as /notes/{id}
    app.include_router(notes_router)
    app.include_router(tasks_router)
    app.include_router(interests_router)
    app.include_router(recommendations_router)
    return app


app = create_app()
