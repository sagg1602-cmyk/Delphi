"""Response format for POST /recommendations/generate."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["task", "note", "interest", "resource"]
    id: int | str
    label: str = Field(min_length=1)


class RecommendationAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["open_task", "open_url"]
    target: int | str


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    type: Literal["study", "discovery"]
    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    estimated_minutes: int = Field(gt=0)
    evidence: list[Evidence] = Field(min_length=1)
    action: RecommendationAction


class GenerateRecommendationsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendations: list[Recommendation] = Field(
        default_factory=list,
        max_length=2,
    )