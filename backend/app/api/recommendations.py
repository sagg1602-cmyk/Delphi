"""Generate recommendations on demand without saving them."""

from fastapi import APIRouter, Depends, HTTPException, Request

from database import get_current_user_id
from app.schemas.recommendations import GenerateRecommendationsResponse
from app.services.recommendations.context import build_user_context
from app.services.recommendations.engine import generate_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)


def get_recommendation_context(
    request: Request,
    user_id: int = Depends(get_current_user_id),
):
    sources = getattr(
        request.app.state,
        "recommendation_sources",
        None,
    )
    if sources is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation data sources are not configured.",
        )

    with request.app.state.engine.connect() as db:
        return build_user_context(
            db,
            user_id,
            sources=sources,
        )


@router.post(
    "/generate",
    response_model=GenerateRecommendationsResponse,
)
def generate(context: dict = Depends(get_recommendation_context)):
    return {
        "recommendations": generate_recommendations(context),
    }