import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings
from app.routers import estimates, health
from app.schemas import BatchEstimateRequest, PropertyFeatures
from app.services.prediction_client import PredictionService

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logging.getLogger().setLevel(log_level)


def _describe_schema(schema: dict, definitions: dict) -> dict:
    reference = schema.get("$ref")
    if reference:
        return _describe_schema(definitions[reference.rsplit("/", 1)[-1]], definitions)

    description = {"type": schema.get("type", "object")}
    labels = {
        "exclusiveMinimum": "greater than",
        "minimum": "at least",
        "exclusiveMaximum": "less than",
        "maximum": "at most",
        "minItems": "at least",
        "maxItems": "at most",
    }
    constraints = []
    for key, label in labels.items():
        if key in schema:
            value = schema[key]
            unit = " item" if value == 1 else " items"
            constraints.append(
                f"{label} {value}{unit}" if key.endswith("Items") else f"{label} {value}"
            )
    if constraints:
        description["constraints"] = constraints

    properties = schema.get("properties")
    if properties:
        required = set(schema.get("required", []))
        description["fields"] = [
            {
                "name": name,
                **_describe_schema(field_schema, definitions),
                "required": name in required,
            }
            for name, field_schema in properties.items()
        ]
    if "items" in schema:
        description["items"] = _describe_schema(schema["items"], definitions)
    if schema.get("additionalProperties") is False:
        description["additional_fields_allowed"] = False
    return description


def _field_path(location: tuple) -> str:
    parts = []
    for item in location:
        if item == "body":
            continue
        if isinstance(item, int):
            parts[-1] = f"{parts[-1]}[{item}]" if parts else f"[{item}]"
        else:
            parts.append(str(item))
    return ".".join(parts) or "request body"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        async with httpx.AsyncClient(
            base_url=settings.prediction_api_url,
            timeout=settings.request_timeout,
        ) as client:
            application.state.prediction_service = PredictionService(client)
            yield

    application = FastAPI(
        title="Value Estimator API",
        description="Property estimate and comparison API backed by the house-price model.",
        version="0.1.0",
        lifespan=lifespan,
    )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_models = {
            "/api/v1/estimates": PropertyFeatures,
            "/api/v1/estimates/batch": BatchEstimateRequest,
        }
        request_model = request_models.get(request.url.path)
        expected = None
        if request_model is not None:
            schema = request_model.model_json_schema()
            expected = _describe_schema(schema, schema.get("$defs", {}))

        return JSONResponse(
            status_code=422,
            content={
                "message": "Request data is invalid.",
                "errors": [
                    {"field": _field_path(error["loc"]), "message": error["msg"]}
                    for error in exc.errors()
                ],
                "expected": expected,
            },
        )

    application.include_router(health.router)
    application.include_router(estimates.router)
    return application


app = create_app()