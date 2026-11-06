"""Note routes."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.engine import Connection

from app.api.deps import get_current_user_id, get_db
from app.repositories.notes import create_note as save_note
from app.repositories.notes import delete_note as remove_note
from app.repositories.notes import get_note as fetch_note
from app.repositories.notes import list_notes as fetch_notes
from app.schemas import NoteCreate, NoteOut

router = APIRouter()


@router.post("/notes", status_code=201, response_model=NoteOut)
def create_note(
    body: NoteCreate,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    return save_note(
        db,
        user_id,
        body.title,
        body.content,
        body.source_type,
        body.source_path,
    )


@router.get("/notes", response_model=list[NoteOut])
def list_notes(
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> list[dict]:
    return fetch_notes(db, user_id)


@router.get("/notes/{note_id}", response_model=NoteOut)
def get_note(
    note_id: int,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    row = fetch_note(db, user_id, note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return row


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Response:
    if not remove_note(db, user_id, note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return Response(status_code=204)
