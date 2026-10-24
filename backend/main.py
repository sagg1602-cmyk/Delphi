"""Delphi Week 1 API: health, notes, and tasks for the seeded dev user."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from database import database_url, get_current_user_id, init_schema, make_engine
from models import NoteCreate, NoteOut, TaskCreate, TaskOut

def create_app(engine: Engine | None = None) -> FastAPI:
    """Build the API. Pass an engine to point tests at delphi_test."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app_engine = engine
        owns_engine = app_engine is None
        if app_engine is None:
            app_engine = make_engine(database_url())
        app.state.engine = app_engine
        try:
            init_schema(app_engine)
            yield
        finally:
            if owns_engine:
                app_engine.dispose()

    app = FastAPI(title="Delphi API (Week 1, dev only)", lifespan=lifespan)
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

    @app.get("/health", response_model=None)
    def health(request: Request) -> JSONResponse | dict[str, str]:
        try:
            with request.app.state.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except OperationalError:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "database": "unreachable"},
            )
        return {"status": "ok", "database": "ok"}

    @app.post("/notes", status_code=201, response_model=NoteOut)
    def create_note(
        body: NoteCreate,
        request: Request,
        user_id: int = Depends(get_current_user_id),
    ) -> dict:
        with request.app.state.engine.begin() as conn:
            row = conn.execute(
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
                    "title": body.title,
                    "content": body.content,
                    "source_type": body.source_type,
                },
            ).mappings().one()
        return dict(row)

    @app.get("/notes", response_model=list[NoteOut])
    def list_notes(
        request: Request,
        user_id: int = Depends(get_current_user_id),
    ) -> list[dict]:
        with request.app.state.engine.connect() as conn:
            rows = conn.execute(
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
            ).mappings().all()
        return [dict(row) for row in rows]

    @app.post("/tasks", status_code=201, response_model=TaskOut)
    def create_task(
        body: TaskCreate,
        request: Request,
        user_id: int = Depends(get_current_user_id),
    ) -> dict:
        with request.app.state.engine.begin() as conn:
            row = conn.execute(
                text(
                    """
                    INSERT INTO tasks (user_id, title, due_date, status)
                    VALUES (:user_id, :title, :due_date, :status)
                    RETURNING id, user_id, title, due_date, status,
                              created_at, updated_at
                    """
                ),
                {
                    "user_id": user_id,
                    "title": body.title,
                    "due_date": body.due_date,
                    "status": body.status,
                },
            ).mappings().one()
        return dict(row)

    @app.get("/tasks", response_model=list[TaskOut])
    def list_tasks(
        request: Request,
        user_id: int = Depends(get_current_user_id),
    ) -> list[dict]:
        with request.app.state.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT id, user_id, title, due_date, status,
                           created_at, updated_at
                    FROM tasks
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC, id DESC
                    """
                ),
                {"user_id": user_id},
            ).mappings().all()
        return [dict(row) for row in rows]

    return app


app = create_app()
