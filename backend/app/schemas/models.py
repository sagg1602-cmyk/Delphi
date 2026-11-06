"""Pydantic request and response models. Tables live in schema.sql."""

from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

# Single home for allowed task statuses. Add a value here to allow it in the API.
TaskStatus = Literal["todo", "done"]


def iso_utc(value: datetime) -> str:
    """ISO 8601 timestamp in UTC, with a Z suffix."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    text = value.isoformat(timespec="microseconds")
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text


class TrimmedTitle(BaseModel):
    """Shared title rule. Create models extend this; Week 2 update models can too."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class NoteFields(TrimmedTitle):
    """Note fields shared by create requests and, later, update requests."""

    content: str = Field(default="", max_length=50_000)
    source_type: str = Field(default="manual", min_length=1, max_length=50)


class NoteCreate(NoteFields):
    """Body for POST /notes. Unknown fields, including user_id, are rejected."""


class NoteOut(BaseModel):
    """Saved note. Field order matches the shared contract."""

    id: int
    user_id: int
    title: str
    content: str
    source_type: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return iso_utc(value)


class TaskFields(TrimmedTitle):
    """Task fields shared by create requests and, later, update requests."""

    due_date: date | None = None
    status: TaskStatus = "todo"


class TaskCreate(TaskFields):
    """Body for POST /tasks. Task fields are proposed, confirm with Manny and Sebastian."""


class TaskOut(BaseModel):
    """Saved task. Field order matches the shared contract."""

    id: int
    user_id: int
    title: str
    due_date: date | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return iso_utc(value)
