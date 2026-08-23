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

import os
import secrets
import sys
from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.helpers import fmt_inr, get_price_tier

# ── App Setup ─────────────────────────────────────────────────────────────

app = FastAPI(title="AutoIntel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "autointel-api"}


@app.get("/api/v1/cars/stats", dependencies=[Depends(verify_api_key)])
async def car_stats():
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


@app.get("/api/v1/cars/brands", dependencies=[Depends(verify_api_key)])
async def car_brands():
    """Return list of available car brands."""
    df = _load_cars_df()
    brands = sorted(df["Brand"].unique().tolist()) if "Brand" in df.columns else []
    return {"brands": brands}


@app.get("/api/v1/cars/fuel-types", dependencies=[Depends(verify_api_key)])
async def fuel_types():
    """Return list of available fuel types."""
    df = _load_cars_df()
    types = sorted(df["Fuel_Type"].unique().tolist()) if "Fuel_Type" in df.columns else []
    return {"fuel_types": types}


@app.post("/api/v1/predict", dependencies=[Depends(verify_api_key)])
async def predict_price(request: Request):
    """Predict car price based on inputs.

    Body JSON fields:
        brand, model, year, km_driven, fuel_type, transmission
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Validate required fields
    required = ["brand", "model", "year", "km_driven", "fuel_type", "transmission"]
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fields: {missing}")

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


# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
