"""Extended tests for helpers module — formatting, classification, prediction."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from app.helpers import (
    CURRENT_YEAR,
    fmt_inr,
    get_fuel_simple,
    get_price_tier,
    get_company_tier,
    make_prediction,
    price_tier_badge,
)


class TestFmtInr:
    """Tests for Indian Rupee formatting."""

    def test_crores(self) -> None:
        assert fmt_inr(1_50_00_000) == "₹1.50Cr"

    def test_lakhs(self) -> None:
        assert fmt_inr(8_50_000) == "₹8.5L"

    def test_thousands(self) -> None:
        assert fmt_inr(45_000) == "₹45,000"

    def test_zero(self) -> None:
        assert fmt_inr(0) == "₹0"

    def test_exact_boundary_cr(self) -> None:
        assert fmt_inr(1_00_00_000) == "₹1.00Cr"

    def test_exact_boundary_lakh(self) -> None:
        assert fmt_inr(1_00_000) == "₹1.0L"


class TestPriceTier:
    """Tests for price tier classification."""

    def test_budget(self) -> None:
        tier, cls = get_price_tier(2_00_000)
        assert tier == "Budget"
        assert cls == "badge-budget"

    def test_midrange(self) -> None:
        tier, cls = get_price_tier(5_00_000)
        assert tier == "Mid-range"
        assert cls == "badge-mid"

    def test_premium(self) -> None:
        tier, cls = get_price_tier(12_00_000)
        assert tier == "Premium"
        assert cls == "badge-premium"

    def test_luxury(self) -> None:
        tier, cls = get_price_tier(25_00_000)
        assert tier == "Luxury"
        assert cls == "badge-luxury"


class TestCompanyTier:
    """Tests for company tier classification."""

    def test_luxury_brand(self) -> None:
        assert get_company_tier(20_00_000) == "Luxury"

    def test_premium_brand(self) -> None:
        assert get_company_tier(8_00_000) == "Premium"

    def test_mid_brand(self) -> None:
        assert get_company_tier(4_00_000) == "Mid"

    def test_budget_brand(self) -> None:
        assert get_company_tier(2_00_000) == "Budget"


class TestFuelSimple:
    """Tests for fuel type simplification."""

    def test_petrol(self) -> None:
        assert get_fuel_simple("Petrol") == "Petrol"

    def test_diesel(self) -> None:
        assert get_fuel_simple("Diesel") == "Diesel"

    def test_cng(self) -> None:
        assert get_fuel_simple("CNG") == "Alternative"

    def test_lpg(self) -> None:
        assert get_fuel_simple("LPG") == "Alternative"

    def test_electric(self) -> None:
        assert get_fuel_simple("Electric") == "Alternative"


class TestPriceTierBadge:
    """Tests for HTML badge generation."""

    def test_contains_span(self) -> None:
        badge = price_tier_badge(5_00_000)
        assert "<span" in badge
        assert "</span>" in badge

    def test_budget_badge(self) -> None:
        badge = price_tier_badge(1_00_000)
        assert "badge-budget" in badge
        assert "Budget" in badge


class TestMakePrediction:
    """Tests for ML prediction wrapper."""

    def test_with_mock_model(self) -> None:
        model = MagicMock()
        model.predict.return_value = np.array([np.log1p(5_00_000)])
        preprocessor = MagicMock()
        preprocessor.transform.return_value = np.array([[1, 2, 3]])
        result = make_prediction(model, pd.DataFrame({"km_driven": [50000]}), preprocessor)
        assert abs(result - 5_00_000) < 1

    def test_with_realistic_input(self) -> None:
        model = MagicMock()
        model.predict.return_value = np.array([np.log1p(3_50_000)])
        preprocessor = MagicMock()
        preprocessor.transform.return_value = np.array([[1, 2, 3, 4, 5, 6]])
        df = pd.DataFrame({
            "km_driven": [30000],
            "fuel_type": ["Petrol"],
            "seller_type": ["Dealer"],
            "transmission": ["Manual"],
            "owner": [1],
            "age": [3],
        })
        result = make_prediction(model, df, preprocessor)
        assert abs(result - 3_50_000) < 1


class TestCurrentYear:
    """Tests for CURRENT_YEAR constant."""

    def test_is_int(self) -> None:
        assert isinstance(CURRENT_YEAR, int)

    def test_is_recent(self) -> None:
        assert CURRENT_YEAR >= 2024
