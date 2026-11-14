"""Note routes."""

from fastapi import APIRouter, Depends, Request

from app.core.database import get_current_user_id
from app.repositories.notes import create_note as save_note
from app.repositories.notes import list_notes as fetch_notes
from app.schemas import NoteCreate, NoteOut

router = APIRouter()


@router.post("/notes", status_code=201, response_model=NoteOut)
def create_note(
    body: NoteCreate,
    request: Request,
    user_id: int = Depends(get_current_user_id),
) -> dict:
    with request.app.state.engine.begin() as conn:
        return save_note(conn, user_id, body.title, body.content, body.source_type)


@router.get("/notes", response_model=list[NoteOut])
def list_notes(
    request: Request,
    user_id: int = Depends(get_current_user_id),
) -> list[dict]:
    with request.app.state.engine.connect() as conn:
        return fetch_notes(conn, user_id)
