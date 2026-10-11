from fastapi import APIRouter, Depends

from app.dependencies import get_prediction_service
from app.schemas import (
    BatchEstimateRequest,
    BatchEstimateResponse,
    EstimateResponse,
    PropertyFeatures,
)
from app.services.prediction_client import PredictionService

router = APIRouter(prefix="/api/v1/estimates", tags=["estimates"])


@router.post("", response_model=EstimateResponse)
async def estimate_property(
    house: PropertyFeatures,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> EstimateResponse:
    result = await prediction_service.predict_one(house)
    return EstimateResponse(**result)


@router.post("/batch", response_model=BatchEstimateResponse)
async def estimate_properties(
    request: BatchEstimateRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> BatchEstimateResponse:
    result = await prediction_service.predict_batch(request.houses)
    return BatchEstimateResponse(**result)