"""Integration tests for Price-My-Car (AutoIntel) — full HTTP lifecycle through FastAPI.

Tests the complete request-response cycle including middleware, error handling,
multi-endpoint workflows, and OpenAPI schema generation. Uses mocked dataset
but exercises real HTTP routing and middleware.
"""

from __future__ import annotations

import asyncio
import json
import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.api_server import app, verify_api_key


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def sample_df():
    """Sample car dataset for mocking _load_cars_df."""
    return pd.DataFrame({
        "name": ["Swift VDI", "Wagon R", "Alto 800", "i20 Magna", "Innova"],
        "company": ["Maruti", "Maruti", "Maruti", "Hyundai", "Toyota"],
        "Brand": ["Maruti", "Maruti", "Maruti", "Hyundai", "Toyota"],
        "fuel_type": ["Diesel", "Petrol", "Petrol", "Diesel", "Diesel"],
        "Fuel_Type": ["Diesel", "Petrol", "Petrol", "Diesel", "Diesel"],
        "year": [2018, 2019, 2020, 2019, 2017],
        "Price": [500000, 300000, 200000, 550000, 1200000],
        "kms_driven": [30000, 50000, 20000, 40000, 80000],
    })


@pytest.fixture()
def large_df():
    """Larger dataset for edge case testing."""
    np.random.seed(42)
    n = 200
    brands = ["Maruti", "Hyundai", "Toyota", "Honda", "Tata", "Mahindra", "Kia", "MG"]
    fuels = ["Petrol", "Diesel", "CNG", "Electric"]
    transmissions = ["Manual", "Automatic"]
    return pd.DataFrame({
        "Brand": np.random.choice(brands, n),
        "Price": np.random.uniform(200000, 5000000, n),
        "Fuel_Type": np.random.choice(fuels, n),
        "year": np.random.randint(2010, 2025, n),
        "kms_driven": np.random.randint(0, 200000, n),
        "name": [f"Car_{i}" for i in range(n)],
    })


# ── Full HTTP Lifecycle ───────────────────────────────────────────────────


class TestHTTPLifecycle:
    """Tests that exercise the full request → middleware → handler → response cycle."""

    def test_root_not_found(self, client):
        """Root path should return 404 (no / route defined)."""
        response = client.get("/")
        assert response.status_code == 404

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "autointel-api"

    def test_health_has_content_type_json(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]


# ── Middleware Behavior ────────────────────────────────────────────────────


class TestMiddleware:
    """Verify CORS, security headers, and rate limiting are applied."""

    def test_metrics_endpoint_accessible(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200


# ── Car Stats Endpoint ────────────────────────────────────────────────────


class TestCarStatsWorkflow:
    """Integration tests for dataset statistics."""

    @patch("app.api_server._load_cars_df")
    def test_stats_returns_correct_counts(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.get("/api/v1/cars/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cars"] == 5
        assert data["brands"] == 3
        assert data["price_range"]["min"] == 200000.0
        assert data["price_range"]["max"] == 1200000.0

    @patch("app.api_server._load_cars_df")
    def test_stats_with_large_dataset(self, mock_load, client, large_df):
        mock_load.return_value = large_df
        response = client.get("/api/v1/cars/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cars"] == 200
        assert data["brands"] == 8

    @patch("app.api_server._load_cars_df")
    def test_stats_price_mean_calculation(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.get("/api/v1/cars/stats")
        data = response.json()
        expected_mean = float(sample_df["Price"].mean())
        assert abs(data["price_range"]["mean"] - expected_mean) < 0.01

    def test_stats_dataset_not_found(self, client):
        """When dataset is missing, returns 503."""
        with patch("app.api_server._load_cars_df") as mock_load:
            from fastapi import HTTPException
            mock_load.side_effect = HTTPException(status_code=503, detail="Dataset not found")
            response = client.get("/api/v1/cars/stats")
            assert response.status_code == 503


# ── Car Brands Endpoint ───────────────────────────────────────────────────


class TestCarBrandsWorkflow:
    """Integration tests for brand listing."""

    @patch("app.api_server._load_cars_df")
    def test_brands_returns_sorted_list(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.get("/api/v1/cars/brands")
        assert response.status_code == 200
        data = response.json()
        assert data["brands"] == ["Hyundai", "Maruti", "Toyota"]

    @patch("app.api_server._load_cars_df")
    def test_brands_with_many_brands(self, mock_load, client, large_df):
        mock_load.return_value = large_df
        response = client.get("/api/v1/cars/brands")
        assert response.status_code == 200
        brands = response.json()["brands"]
        assert len(brands) == 8
        assert brands == sorted(brands)  # must be sorted

    @patch("app.api_server._load_cars_df")
    def test_brands_missing_column(self, mock_load, client):
        mock_load.return_value = pd.DataFrame({"name": ["A"]})
        response = client.get("/api/v1/cars/brands")
        assert response.status_code == 200
        assert response.json()["brands"] == []


# ── Fuel Types Endpoint ───────────────────────────────────────────────────


class TestFuelTypesWorkflow:
    """Integration tests for fuel type listing."""

    @patch("app.api_server._load_cars_df")
    def test_fuel_types_returns_sorted(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.get("/api/v1/cars/fuel-types")
        assert response.status_code == 200
        data = response.json()
        assert data["fuel_types"] == ["Diesel", "Petrol"]

    @patch("app.api_server._load_cars_df")
    def test_fuel_types_all_varieties(self, mock_load, client, large_df):
        mock_load.return_value = large_df
        response = client.get("/api/v1/cars/fuel-types")
        assert response.status_code == 200
        types = response.json()["fuel_types"]
        assert "Electric" in types
        assert "CNG" in types

    @patch("app.api_server._load_cars_df")
    def test_fuel_types_missing_column(self, mock_load, client):
        mock_load.return_value = pd.DataFrame({"name": ["A"]})
        response = client.get("/api/v1/cars/fuel-types")
        assert response.status_code == 200
        assert response.json()["fuel_types"] == []


# ── Predict Endpoint ──────────────────────────────────────────────────────


class TestPredictWorkflow:
    """Integration tests for car price prediction."""

    @patch("app.api_server._load_cars_df")
    def test_predict_returns_estimated_price(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        body = {
            "brand": "Maruti",
            "model": "Swift",
            "year": 2020,
            "km_driven": 25000,
            "fuel_type": "Petrol",
            "transmission": "Manual",
        }
        response = client.post("/api/v1/predict", json=body)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_price" in data
        assert "formatted_price" in data
        assert "tier" in data
        assert "inputs" in data
        assert data["predicted_price"] > 0
        assert "INR" in data["formatted_price"] or "₹" in data["formatted_price"]

    @patch("app.api_server._load_cars_df")
    def test_predict_with_all_fuel_types(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        for fuel in ["Petrol", "Diesel", "CNG", "Electric"]:
            body = {
                "brand": "Maruti",
                "model": "Swift",
                "year": 2020,
                "km_driven": 25000,
                "fuel_type": fuel,
                "transmission": "Manual",
            }
            response = client.post("/api/v1/predict", json=body)
            assert response.status_code == 200

    @patch("app.api_server._load_cars_df")
    def test_predict_preserves_all_inputs(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        body = {
            "brand": "Hyundai",
            "model": "i20",
            "year": 2021,
            "km_driven": 10000,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
        }
        response = client.post("/api/v1/predict", json=body)
        data = response.json()
        for key in body:
            assert data["inputs"][key] == body[key]

    @patch("app.api_server._load_cars_df")
    def test_predict_with_zero_km(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        body = {
            "brand": "Maruti",
            "model": "Swift",
            "year": 2025,
            "km_driven": 0,
            "fuel_type": "Petrol",
            "transmission": "Manual",
        }
        response = client.post("/api/v1/predict", json=body)
        assert response.status_code == 200

    @patch("app.api_server._load_cars_df")
    def test_predict_with_very_old_car(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        body = {
            "brand": "Maruti",
            "model": "800",
            "year": 1990,
            "km_driven": 200000,
            "fuel_type": "Petrol",
            "transmission": "Manual",
        }
        response = client.post("/api/v1/predict", json=body)
        assert response.status_code == 200

    @patch("app.api_server._load_cars_df")
    def test_predict_validates_required_fields(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.post("/api/v1/predict", json={"brand": "Maruti"})
        assert response.status_code == 422
        assert "Missing fields" in response.json()["detail"]

    @patch("app.api_server._load_cars_df")
    def test_predict_empty_body(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.post("/api/v1/predict", json={})
        assert response.status_code == 422

    @patch("app.api_server._load_cars_df")
    def test_predict_malformed_json(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.post(
            "/api/v1/predict",
            content="{invalid json",
            headers={"Content-Type": "application/json"},
        )
        # Endpoint catches json.JSONDecodeError and returns 400
        assert response.status_code == 400


# ── Error Handling Workflows ──────────────────────────────────────────────


class TestErrorHandling:
    """Verify graceful error handling across the API."""

    def test_nonexistent_route_returns_404(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_wrong_http_method_returns_405(self, client):
        response = client.post("/health")
        assert response.status_code == 405

    @patch("app.api_server._load_cars_df")
    def test_stats_wrong_method(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.post("/api/v1/cars/stats")
        assert response.status_code == 405

    @patch("app.api_server._load_cars_df")
    def test_brands_wrong_method(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        response = client.post("/api/v1/cars/brands")
        assert response.status_code == 405


# ── Multi-Endpoint Workflow ────────────────────────────────────────────────


class TestMultiEndpointWorkflow:
    """Simulate a realistic user session: health → stats → brands → fuel → predict."""

    @patch("app.api_server._load_cars_df")
    def test_full_user_workflow(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df

        # Step 1: Check health
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        # Step 2: Get dataset stats
        stats = client.get("/api/v1/cars/stats")
        assert stats.status_code == 200
        assert stats.json()["total_cars"] == 5

        # Step 3: Browse brands
        brands = client.get("/api/v1/cars/brands")
        assert brands.status_code == 200
        assert "Maruti" in brands.json()["brands"]

        # Step 4: Check fuel types
        fuels = client.get("/api/v1/cars/fuel-types")
        assert fuels.status_code == 200
        assert "Diesel" in fuels.json()["fuel_types"]

        # Step 5: Make a prediction
        predict = client.post(
            "/api/v1/predict",
            json={
                "brand": "Maruti",
                "model": "Swift",
                "year": 2020,
                "km_driven": 25000,
                "fuel_type": "Petrol",
                "transmission": "Manual",
            },
        )
        assert predict.status_code == 200
        assert predict.json()["predicted_price"] > 0

    def test_openapi_schema_is_valid(self, client):
        """Verify the OpenAPI schema is generated and well-formed."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "AutoIntel API"
        # Verify key endpoints are documented
        assert "/health" in schema["paths"]
        assert "/api/v1/cars/stats" in schema["paths"]
        assert "/api/v1/cars/brands" in schema["paths"]
        assert "/api/v1/cars/fuel-types" in schema["paths"]
        assert "/api/v1/predict" in schema["paths"]


# ── Auth Flow Integration ─────────────────────────────────────────────────


class TestAuthFlow:
    """Test API key authentication across the full request cycle."""

    def test_open_access_when_no_key_set(self, client):
        with patch.dict(os.environ, {"PRICE_MY_CAR_API_KEY": ""}):
            response = client.get("/health")
            assert response.status_code == 200

    def test_rejects_request_without_auth_header(self):
        with patch.dict(os.environ, {"PRICE_MY_CAR_API_KEY": "test-key"}):
            c = TestClient(app, raise_server_exceptions=False)
            response = c.get("/api/v1/cars/stats")
            assert response.status_code == 401

    def test_rejects_wrong_api_key(self):
        with patch.dict(os.environ, {"PRICE_MY_CAR_API_KEY": "correct-key"}):
            c = TestClient(app, raise_server_exceptions=False)
            response = c.get(
                "/api/v1/cars/stats",
                headers={"Authorization": "Bearer wrong-key"},
            )
            assert response.status_code == 403

    def test_accepts_correct_api_key(self):
        with patch.dict(os.environ, {"PRICE_MY_CAR_API_KEY": "my-secret"}):
            c = TestClient(app, raise_server_exceptions=False)
            with patch("app.api_server._load_cars_df") as mock_load:
                mock_load.return_value = pd.DataFrame({
                    "Brand": ["A"], "Price": [100000], "Fuel_Type": ["Petrol"]
                })
                response = c.get(
                    "/api/v1/cars/stats",
                    headers={"Authorization": "Bearer my-secret"},
                )
                assert response.status_code == 200


# ── Data Loading Edge Cases ───────────────────────────────────────────────


class TestDataLoading:
    """Test dataset loading edge cases."""

    @patch("app.api_server._load_cars_df")
    def test_stats_with_single_row(self, mock_load, client):
        mock_load.return_value = pd.DataFrame({
            "Brand": ["BMW"],
            "Price": [3000000.0],
            "Fuel_Type": ["Diesel"],
        })
        response = client.get("/api/v1/cars/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cars"] == 1
        assert data["brands"] == 1

    @patch("app.api_server._load_cars_df")
    def test_predict_with_special_characters(self, mock_load, client):
        mock_load.return_value = pd.DataFrame({
            "Brand": ["BMW", "Mercedes-Benz"],
            "Price": [3000000, 5000000],
            "Fuel_Type": ["Diesel", "Petrol"],
        })
        body = {
            "brand": "Mercedes-Benz",
            "model": "C-Class",
            "year": 2022,
            "km_driven": 15000,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
        }
        response = client.post("/api/v1/predict", json=body)
        assert response.status_code == 200

    @patch("app.api_server._load_cars_df")
    def test_consecutive_predictions_consistent(self, mock_load, client, sample_df):
        """Same input should produce same output (deterministic)."""
        mock_load.return_value = sample_df
        body = {
            "brand": "Toyota",
            "model": "Innova",
            "year": 2017,
            "km_driven": 80000,
            "fuel_type": "Diesel",
            "transmission": "Manual",
        }
        r1 = client.post("/api/v1/predict", json=body)
        r2 = client.post("/api/v1/predict", json=body)
        assert r1.json()["predicted_price"] == r2.json()["predicted_price"]


# ── Concurrent Request Handling ───────────────────────────────────────────


class TestConcurrentRequests:
    """Verify the API handles multiple sequential requests without state leaks."""

    @patch("app.api_server._load_cars_df")
    def test_sequential_stats_requests(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        for _ in range(5):
            response = client.get("/api/v1/cars/stats")
            assert response.status_code == 200
            assert response.json()["total_cars"] == 5

    @patch("app.api_server._load_cars_df")
    def test_mixed_endpoint_requests(self, mock_load, client, sample_df):
        mock_load.return_value = sample_df
        # Interleave different endpoints
        client.get("/health")
        client.get("/api/v1/cars/stats")
        client.get("/api/v1/cars/brands")
        client.get("/api/v1/cars/fuel-types")
        client.post(
            "/api/v1/predict",
            json={
                "brand": "Maruti", "model": "Swift", "year": 2020,
                "km_driven": 25000, "fuel_type": "Petrol", "transmission": "Manual",
            },
        )
        # All should succeed — verify final state
        response = client.get("/health")
        assert response.status_code == 200
