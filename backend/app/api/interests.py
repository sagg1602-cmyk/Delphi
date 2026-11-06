"""Interest routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user_id, get_db
from app.repositories.interests import create_interest as save_interest
from app.repositories.interests import list_interests as fetch_interests
from app.repositories.interests import set_interest_active
from app.schemas import InterestCreate, InterestOut, InterestUpdate

router = APIRouter()


@router.post("/interests", status_code=201, response_model=InterestOut)
def create_interest(
    body: InterestCreate,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    try:
        return save_interest(db, user_id, body.name)
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Interest already exists") from exc


@router.get("/interests", response_model=list[InterestOut])
def list_interests(
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> list[dict]:
    return fetch_interests(db, user_id)


@router.patch("/interests/{interest_id}", response_model=InterestOut)
def update_interest(
    interest_id: int,
    body: InterestUpdate,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    row = set_interest_active(db, user_id, interest_id, body.active)
    if row is None:
        raise HTTPException(status_code=404, detail="Interest not found")
    return row
