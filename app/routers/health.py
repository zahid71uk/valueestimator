from fastapi import APIRouter, Depends

from app.dependencies import get_prediction_service
from app.schemas import HealthResponse
from app.services.prediction_client import PredictionService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> HealthResponse:
    available = await prediction_service.is_available()
    return HealthResponse(
        status="ok" if available else "degraded",
        prediction_api_available=available,
    )