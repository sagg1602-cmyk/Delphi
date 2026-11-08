"""Note search route."""

from fastapi import APIRouter, Depends, Query, Request

from app.core.database import get_current_user_id
from app.services.memory.retrieval import retrieve_notes

router = APIRouter()


@router.get("/notes/search")
def search_notes(
    request: Request,
    q: str = Query("", description="What to search for"),
    limit: int = Query(5, ge=1, le=20),
    user_id: int = Depends(get_current_user_id),
) -> list[dict]:
    with request.app.state.engine.connect() as conn:
        return retrieve_notes(conn, user_id, q, limit)
