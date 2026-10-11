from pydantic import BaseModel, ConfigDict, Field


MAX_BATCH_SIZE = 100


class PropertyFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    square_footage: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: float = Field(ge=0)
    year_built: int = Field(ge=1800, le=2100)
    lot_size: float = Field(gt=0)
    distance_to_city_center: float = Field(ge=0)
    school_rating: float = Field(ge=0, le=10)


class BatchEstimateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    houses: list[PropertyFeatures] = Field(min_length=1, max_length=MAX_BATCH_SIZE)


class EstimateResponse(BaseModel):
    predicted_price: float


class BatchEstimateResponse(BaseModel):
    predictions: list[float]
    count: int


class HealthResponse(BaseModel):
    status: str
    prediction_api_available: bool