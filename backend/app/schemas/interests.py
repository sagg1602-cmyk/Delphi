"""Interest request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.schemas.common import iso_utc


class InterestCreate(BaseModel):
    """Body for POST /interests."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class InterestUpdate(BaseModel):
    """Body for PATCH /interests/{id}. Sends active true or false."""

    model_config = ConfigDict(extra="forbid")

    active: bool


class InterestOut(BaseModel):
    """Saved interest."""

    id: int
    user_id: int
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return iso_utc(value)
