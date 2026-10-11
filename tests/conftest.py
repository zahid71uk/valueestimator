import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_prediction_service
from app.main import create_app


class FakePredictionService:
    async def predict_one(self, house):
        return {"predicted_price": 325000.0}

    async def predict_batch(self, houses):
        predictions = [325000.0 + index * 10000 for index, _ in enumerate(houses)]
        return {"predictions": predictions, "count": len(predictions)}

    async def is_available(self):
        return True


@pytest.fixture
def client():
    application = create_app()
    application.dependency_overrides[get_prediction_service] = (
        lambda: FakePredictionService()
    )
    with TestClient(application) as test_client:
        yield test_client