import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    prediction_api_url: str = "http://127.0.0.1:8000"
    request_timeout: float = 5.0

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            prediction_api_url=os.getenv(
                "PRICE_PREDICTION_API_URL", cls.prediction_api_url
            ).rstrip("/"),
            request_timeout=float(os.getenv("PREDICTION_API_TIMEOUT", "5")),
        )