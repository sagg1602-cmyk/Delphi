"""Task routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from app.api.deps import get_current_user_id, get_db
from app.repositories.tasks import create_task as save_task
from app.repositories.tasks import list_tasks as fetch_tasks
from app.repositories.tasks import update_task as save_task_changes
from app.schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter()


@router.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(
    body: TaskCreate,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    return save_task(
        db,
        user_id,
        body.title,
        body.due_date,
        body.status,
        body.duration_minutes,
        body.priority,
    )


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> list[dict]:
    return fetch_tasks(db, user_id)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    body: TaskUpdate,
    db: Connection = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No fields to update")
    row = save_task_changes(db, user_id, task_id, changes)
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row
