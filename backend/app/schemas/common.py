"""Shared request rules and timestamp formatting."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    """Shared title rule. Create models extend this."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value
