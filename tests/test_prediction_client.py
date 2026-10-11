import httpx
import pytest
from fastapi import HTTPException

from app.schemas import PropertyFeatures
from app.services.prediction_client import PredictionService


HOUSE = PropertyFeatures(
    square_footage=1550,
    bedrooms=3,
    bathrooms=2,
    year_built=1997,
    lot_size=6800,
    distance_to_city_center=4.1,
    school_rating=7.6,
)


@pytest.mark.anyio
async def test_single_prediction_forwards_payload_to_model_api():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/predict"
        assert request.read()
        return httpx.Response(200, json={"predicted_price": 325000.0})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://model.test"
    ) as client:
        result = await PredictionService(client).predict_one(HOUSE)

    assert result == {"predicted_price": 325000.0}


@pytest.mark.anyio
async def test_upstream_unavailable_becomes_user_readable_503():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://model.test"
    ) as client:
        with pytest.raises(HTTPException) as error:
            await PredictionService(client).predict_one(HOUSE)

    assert error.value.status_code == 503
    assert error.value.detail == "The prediction model is not available right now."


@pytest.mark.anyio
async def test_upstream_timeout_becomes_504():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("upstream timeout", request=request)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://model.test"
    ) as client:
        with pytest.raises(HTTPException) as error:
            await PredictionService(client).predict_one(HOUSE)

    assert error.value.status_code == 504


@pytest.mark.anyio
async def test_malformed_upstream_response_becomes_502():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://model.test"
    ) as client:
        with pytest.raises(HTTPException) as error:
            await PredictionService(client).predict_one(HOUSE)

    assert error.value.status_code == 502
    assert error.value.detail == "The prediction service returned an invalid response."