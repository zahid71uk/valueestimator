# Marketanalysis API

An independently runnable FastAPI service that validates property submissions and calls the existing `PricePredictionModel` API over HTTP. It does not import model code or artifacts.

## Requirements

- Python 3.12 or newer

## Setup and run

From this directory, create a virtual environment and install the API and development dependencies:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:PRICE_PREDICTION_API_URL = "http://127.0.0.1:8000"
$env:PREDICTION_API_TIMEOUT = "5"
uvicorn app.main:app --reload --port 8001
```

Start `PricePredictionModel` first, then set `PRICE_PREDICTION_API_URL` to its base URL. `PREDICTION_API_TIMEOUT` controls the upstream request timeout in seconds. Interactive API docs are at `http://127.0.0.1:8001/docs`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Marketanalysis and upstream model availability |
| POST | `/api/v1/estimates` | Estimate one property |
| POST | `/api/v1/estimates/batch` | Estimate 1–100 properties |

The request fields and constraints match the existing model API: positive square footage and lot size; non-negative bedrooms, bathrooms, and distance; year built from 1800 through 2100; and school rating from 0 through 10. Invalid requests return HTTP 422 with readable field paths, expected types, and constraints. Upstream timeouts and unavailable-model responses are mapped to user-readable HTTP errors.

## Tests

```powershell
python -m pytest -v
```