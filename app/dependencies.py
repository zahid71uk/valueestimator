from fastapi import Request

from app.services.prediction_client import PredictionService


def get_prediction_service(request: Request) -> PredictionService:
    return request.app.state.prediction_service