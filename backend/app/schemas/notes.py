"""Note request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.schemas.common import TrimmedTitle, iso_utc


class NoteFields(TrimmedTitle):
    """Note fields shared by create requests."""

    content: str = Field(default="", max_length=50_000)
    source_type: str = Field(default="manual", min_length=1, max_length=50)


class NoteCreate(NoteFields):
    """Body for POST /notes. Unknown fields, including id and user_id, are rejected."""

    source_path: str | None = Field(default=None, max_length=500)

    @field_validator("source_path", mode="before")
    @classmethod
    def blank_source_path(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value


class NoteOut(BaseModel):
    """Saved note. Field order matches the shared contract."""

    id: int
    user_id: int
    title: str
    content: str
    source_type: str
    source_path: str | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return iso_utc(value)
