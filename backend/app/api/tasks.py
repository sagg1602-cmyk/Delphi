"""Task routes."""

from fastapi import APIRouter, Depends, Request

from app.core.database import get_current_user_id
from app.repositories.tasks import create_task as save_task
from app.repositories.tasks import list_tasks as fetch_tasks
from app.schemas import TaskCreate, TaskOut

router = APIRouter()


@router.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(
    body: TaskCreate,
    request: Request,
    user_id: int = Depends(get_current_user_id),
) -> dict:
    with request.app.state.engine.begin() as conn:
        return save_task(conn, user_id, body.title, body.due_date, body.status)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    request: Request,
    user_id: int = Depends(get_current_user_id),
) -> list[dict]:
    with request.app.state.engine.connect() as conn:
        return fetch_tasks(conn, user_id)
