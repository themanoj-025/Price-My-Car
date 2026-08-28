"""
api_server.py — FastAPI REST API for AutoIntel Car Price Intelligence
=====================================================================
Exposes prediction and data endpoints with optional API key auth.

Usage:
    uvicorn app.api_server:app --host 0.0.0.0 --port 8000

Auth:
    Set PRICE_MY_CAR_API_KEY env var to enable Bearer token auth.
    When unset, all endpoints are open (backward compatible).
"""

import json
import logging
import os
import secrets
import sys
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.helpers import fmt_inr, get_price_tier

try:
    from prometheus_client import Counter, Histogram, generate_latest

    _PROM_AVAILABLE = True
except ImportError:
    _PROM_AVAILABLE = False

# ── Structured Logging ─────────────────────────────────────────────────────

class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for production log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra fields
        for key in ("method", "path", "status_code", "duration_ms", "client_ip"):
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val

        # Include exception info if present
        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, ensure_ascii=False, default=str)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("autointel-api")

# Add structured JSON file handler
try:
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "api.log", encoding="utf-8")
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
except OSError:
    pass  # Non-fatal if logs dir not writable

if _PROM_AVAILABLE:
    PMC_REQUEST_COUNT = Counter(
        "pricecar_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    PMC_REQUEST_LATENCY = Histogram(
        "pricecar_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
    PMC_PREDICTIONS = Counter("pricecar_predictions_total", "Price predictions made")

# ── App Setup ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AutoIntel API",
    description="Car price prediction and dataset analytics API.\n\n"
    "Provides used-car price estimation, dataset statistics, brand/fuel-type listings, "
    "and dataset quality reporting.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "health",
            "description": "Service health check",
        },
        {
            "name": "analytics",
            "description": "Dataset statistics and metadata (brands, fuel types, summary stats)",
        },
        {
            "name": "predictions",
            "description": "Car price prediction based on vehicle attributes",
        },
    ],
)

@app.middleware("http")
async def track_metrics(request, call_next) -> Response:
    import time as _time
    request.state.start_time = _time.time()
    response = await call_next(request)
    if _PROM_AVAILABLE:
        path = request.url.path
        PMC_REQUEST_COUNT.labels(
            method=request.method, endpoint=path, status=response.status_code
        ).inc()
        if hasattr(request.state, "start_time"):
            PMC_REQUEST_LATENCY.labels(method=request.method, endpoint=path).observe(
                _time.time() - request.state.start_time
            )
    return response

_allowed_origins = os.environ.get(
    "PRICE_MY_CAR_CORS_ORIGINS", "http://localhost:8501,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

security = HTTPBearer(auto_error=False)

# ── API v1 Router ──────────────────────────────────────────────────────
v1_router = APIRouter(prefix="/api/v1")

# ── Auth ──────────────────────────────────────────────────────────────────


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> HTTPAuthorizationCredentials:
    """Verify API key from Authorization header. Enabled when PRICE_MY_CAR_API_KEY is set."""
    api_key = os.environ.get("PRICE_MY_CAR_API_KEY", "")
    if not api_key:
        return credentials  # No key configured — open access
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not secrets.compare_digest(credentials.credentials, api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials


# ── Data helpers ──────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_cars_df() -> pd.DataFrame:
    """Load the cleaned car dataset."""
    csv_path = DATA_DIR / "Cleaned_Car_data.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=503, detail="Dataset not found")
    return pd.read_csv(csv_path)


# ── Endpoints ─────────────────────────────────────────────────────────────


@app.get("/health", tags=["health"])
async def health() -> dict[str, object]:
    """Health check endpoint."""
    return {"status": "ok", "service": "autointel-api"}


@v1_router.get("/cars/stats", dependencies=[Depends(verify_api_key)], tags=["analytics"])
async def car_stats() -> dict[str, object]:
    """Return summary statistics of the car dataset."""
    df = _load_cars_df()
    return {
        "total_cars": len(df),
        "brands": int(df["Brand"].nunique()) if "Brand" in df.columns else 0,
        "price_range": {
            "min": float(df["Price"].min()) if "Price" in df.columns else 0,
            "max": float(df["Price"].max()) if "Price" in df.columns else 0,
            "mean": float(df["Price"].mean()) if "Price" in df.columns else 0,
        },
    }


@v1_router.get("/cars/brands", dependencies=[Depends(verify_api_key)], tags=["analytics"])
async def car_brands() -> dict[str, object]:
    """Return list of available car brands."""
    df = _load_cars_df()
    brands = sorted(df["Brand"].unique().tolist()) if "Brand" in df.columns else []
    return {"brands": brands}


@v1_router.get("/cars/fuel-types", dependencies=[Depends(verify_api_key)], tags=["analytics"])
async def fuel_types() -> dict[str, object]:
    """Return list of available fuel types."""
    df = _load_cars_df()
    types = sorted(df["Fuel_Type"].unique().tolist()) if "Fuel_Type" in df.columns else []
    return {"fuel_types": types}


@v1_router.post("/predict", dependencies=[Depends(verify_api_key)], tags=["predictions"])
async def predict_price(request: Request) -> dict[str, object]:
    """Predict car price based on inputs.

    Body JSON fields:
        brand, model, year, km_driven, fuel_type, transmission
    """
    try:
        body = await request.json()
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Validate required fields
    required = ["brand", "model", "year", "km_driven", "fuel_type", "transmission"]
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fields: {missing}")

    if _PROM_AVAILABLE:
        PMC_PREDICTIONS.inc()

    # For now, return a simple estimate based on dataset averages
    # In production, load trained model with joblib.load()
    df = _load_cars_df()
    avg_price = float(df["Price"].mean()) if "Price" in df.columns else 500000

    tier, _badge = get_price_tier(avg_price)

    return {
        "predicted_price": avg_price,
        "formatted_price": fmt_inr(avg_price),
        "tier": tier,
        "inputs": body,
        "note": "Prediction uses dataset average. Train a model for accurate predictions.",
    }


app.include_router(v1_router)


@app.get("/metrics", tags=["health"])
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    if not _PROM_AVAILABLE:
        return {"status": "prometheus_client not installed"}
    return Response(content=generate_latest(), media_type="text/plain")


# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
