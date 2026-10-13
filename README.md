# Value Estimator API

An independently runnable FastAPI service that validates property submissions and calls the existing `PricePredictionModel` API over HTTP. It does not import model code or artifacts.

## Requirements

- Python 3.12 or newer

## Setup and run

```### If you get error when activating virtual environment us ethe below command to bypass policy issue
```### Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

From this directory, create a virtual environment with Python 3.12 (the minimum supported version), then install the API and development dependencies:

```powershell
py -3.12 -m venv .venv312
### If you get error when activating virtual environment us ethe below command to bypass policy issue
### Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv312\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:PRICE_PREDICTION_API_URL = "http://127.0.0.1:8000"
$env:PREDICTION_API_TIMEOUT = "5"
python -m uvicorn app.main:app --reload --port 8001
```

For a newer Python version, replace `3.12` and `.venv312` with that version (for example, `3.14` and `.venv314`). Use a separate virtual environment for each Python version; do not reuse one created by another interpreter.

Start `PricePredictionModel` first, then set `PRICE_PREDICTION_API_URL` to its base URL. `PREDICTION_API_TIMEOUT` controls the upstream request timeout in seconds. Interactive API docs are at `http://127.0.0.1:8001/docs`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Value estimator and upstream model availability |
| POST | `/api/v1/estimates` | Estimate one property |
| POST | `/api/v1/estimates/batch` | Estimate 1–100 properties |

The request fields and constraints match the existing model API: positive square footage and lot size; non-negative bedrooms, bathrooms, and distance; year built from 1800 through 2100; and school rating from 0 through 10. Invalid requests return HTTP 422 with readable field paths, expected types, and constraints. Upstream timeouts and unavailable-model responses are mapped to user-readable HTTP errors.

## Tests

```powershell
python -m pytest -v
```