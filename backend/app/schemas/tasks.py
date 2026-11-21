"""Task request and response schemas."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from app.schemas.common import TrimmedTitle, iso_utc

# Single home for allowed task statuses. Add a value here to allow it in the API.
TaskStatus = Literal["todo", "done"]
Priority = Literal["low", "medium", "high"]


class TaskCreate(TrimmedTitle):
    """Body for POST /tasks."""

    due_date: date | None = None
    status: TaskStatus = "todo"
    duration_minutes: int | None = Field(default=None, ge=1)
    priority: Priority | None = None


class TaskUpdate(BaseModel):
    """Body for PATCH /tasks/{id}. Only fields that are sent are changed."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    due_date: date | None = None
    status: TaskStatus | None = None
    duration_minutes: int | None = Field(default=None, ge=1)
    priority: Priority | None = None

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def reject_null_title_and_status(self) -> "TaskUpdate":
        if "title" in self.model_fields_set and not self.title:
            raise ValueError("title cannot be null")
        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status cannot be null")
        return self


class TaskOut(BaseModel):
    """Saved task. Field order matches the shared contract."""

    id: int
    user_id: int
    title: str
    due_date: date | None
    status: TaskStatus
    duration_minutes: int | None
    priority: Priority | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return iso_utc(value)
