import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import (
    BatchEstimateResponse,
    EstimateResponse,
    PropertyFeatures,
)


class PredictionService:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def predict_one(self, house: PropertyFeatures) -> dict:
        result = await self._post("/predict", house.model_dump(mode="json"))
        try:
            return EstimateResponse.model_validate(result).model_dump()
        except ValidationError as exc:
            raise self._invalid_response() from exc

    async def predict_batch(self, houses: list[PropertyFeatures]) -> dict:
        result = await self._post(
            "/predict/batch",
            {"houses": [house.model_dump(mode="json") for house in houses]},
        )
        try:
            return BatchEstimateResponse.model_validate(result).model_dump()
        except ValidationError as exc:
            raise self._invalid_response() from exc

    async def is_available(self) -> bool:
        try:
            response = await self._client.get("/health")
        except httpx.HTTPError:
            return False
        try:
            payload = response.json()
        except ValueError:
            return False
        return (
            response.is_success
            and isinstance(payload, dict)
            and payload.get("model_loaded") is True
        )

    async def _post(self, path: str, payload: dict) -> dict:
        try:
            response = await self._client.post(path, json=payload)
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail="The prediction service took too long to respond. Please try again.",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail="The prediction service is unavailable. Please try again later.",
            ) from exc

        if response.status_code == 503:
            raise HTTPException(
                status_code=503,
                detail="The prediction model is not available right now.",
            )
        if not response.is_success:
            raise HTTPException(
                status_code=502,
                detail="The prediction service could not process this estimate.",
            )

        try:
            return response.json()
        except ValueError as exc:
            raise self._invalid_response() from exc

    @staticmethod
    def _invalid_response() -> HTTPException:
        return HTTPException(
            status_code=502,
            detail="The prediction service returned an invalid response.",
        )