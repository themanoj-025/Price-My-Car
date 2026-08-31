"""Tests for Price-My-Car: helpers and auth_db pure functions."""

import numpy as np
import pandas as pd

# ── Formatting Helpers ──────────────────────────────────────────────────────


class TestFmtInr:
    """Tests for Indian Rupee formatting."""

    def test_crores(self) -> None:
        from app.helpers import fmt_inr

        assert fmt_inr(1.5e7) == "₹1.50Cr"

    def test_lakhs(self) -> None:
        from app.helpers import fmt_inr

        assert fmt_inr(5e5) == "₹5.0L"

    def test_thousands(self) -> None:
        from app.helpers import fmt_inr

        assert fmt_inr(45000) == "₹45,000"

    def test_small_amount(self) -> None:
        from app.helpers import fmt_inr

        assert fmt_inr(999) == "₹999"


class TestGetPriceTier:
    """Tests for price tier classification."""

    def test_luxury(self) -> None:
        from app.helpers import get_price_tier

        tier, cls = get_price_tier(2_500_000)
        assert tier == "Luxury"
        assert cls == "badge-luxury"

    def test_premium(self) -> None:
        from app.helpers import get_price_tier

        tier, cls = get_price_tier(800_000)
        assert tier == "Premium"
        assert cls == "badge-premium"

    def test_mid_range(self) -> None:
        from app.helpers import get_price_tier

        tier, cls = get_price_tier(300_000)
        assert tier == "Mid-range"
        assert cls == "badge-mid"

    def test_budget(self) -> None:
        from app.helpers import get_price_tier

        tier, cls = get_price_tier(100_000)
        assert tier == "Budget"
        assert cls == "badge-budget"


class TestPriceTierBadge:
    """Tests for HTML badge generation."""

    def test_badge_html(self) -> None:
        from app.helpers import price_tier_badge

        badge = price_tier_badge(2_500_000)
        assert badge.startswith("<span")
        assert "Luxury" in badge
        assert badge.endswith("</span>")


class TestGetCompanyTier:
    """Tests for company tier classification."""

    def test_luxury_brand(self) -> None:
        from app.helpers import get_company_tier

        assert get_company_tier(1_500_000) == "Luxury"

    def test_premium_brand(self) -> None:
        from app.helpers import get_company_tier

        assert get_company_tier(600_000) == "Premium"

    def test_mid_brand(self) -> None:
        from app.helpers import get_company_tier

        assert get_company_tier(300_000) == "Mid"

    def test_budget_brand(self) -> None:
        from app.helpers import get_company_tier

        assert get_company_tier(100_000) == "Budget"


class TestGetFuelSimple:
    """Tests for fuel type grouping."""

    def test_petrol(self) -> None:
        from app.helpers import get_fuel_simple

        assert get_fuel_simple("Petrol") == "Petrol"

    def test_diesel(self) -> None:
        from app.helpers import get_fuel_simple

        assert get_fuel_simple("Diesel") == "Diesel"

    def test_cng_alternative(self) -> None:
        from app.helpers import get_fuel_simple

        assert get_fuel_simple("CNG") == "Alternative"

    def test_lpg_alternative(self) -> None:
        from app.helpers import get_fuel_simple

        assert get_fuel_simple("LPG") == "Alternative"

    def test_electric_alternative(self) -> None:
        from app.helpers import get_fuel_simple

        assert get_fuel_simple("Electric") == "Alternative"


# ── Data Helpers ────────────────────────────────────────────────────────────


class TestGetCarNameOptions:
    """Tests for car name filtering."""

    def test_returns_sorted(self) -> None:
        from app.helpers import get_car_name_options

        df = pd.DataFrame({"company": ["Toyota", "Toyota", "Honda"], "name": ["Camry", "Corolla", "Civic"]})
        result = get_car_name_options(df, "Toyota")
        assert result == ["Camry", "Corolla"]


class TestGetFilteredData:
    """Tests for multi-column filtering."""

    def test_filter_by_company(self) -> None:
        from app.helpers import get_filtered_data

        df = pd.DataFrame({
            "company": ["Toyota", "Honda", "Toyota"],
            "fuel_type": ["Petrol", "Diesel", "Petrol"],
            "year": [2020, 2021, 2022],
            "Price": [500000, 600000, 700000],
            "kms_driven": [10000, 20000, 30000],
        })
        result = get_filtered_data(df, ["Toyota"], ["Petrol"], (2020, 2022), (0, 1e7), (0, 1e6))
        assert len(result) == 2

    def test_filter_by_fuel(self) -> None:
        from app.helpers import get_filtered_data

        df = pd.DataFrame({
            "company": ["Toyota", "Honda"],
            "fuel_type": ["Petrol", "Diesel"],
            "year": [2020, 2021],
            "Price": [500000, 600000],
            "kms_driven": [10000, 20000],
        })
        result = get_filtered_data(df, ["Toyota", "Honda"], ["Diesel"], (2020, 2022), (0, 1e7), (0, 1e6))
        assert len(result) == 1
        assert result.iloc[0]["company"] == "Honda"


# ── Prediction Helpers ──────────────────────────────────────────────────────


class TestComputeDealScore:
    """Tests for deal score computation."""

    def test_fair_price(self) -> None:
        from app.helpers import compute_deal_score

        score = compute_deal_score(100, 100)
        assert score == 50

    def test_undervalued(self) -> None:
        from app.helpers import compute_deal_score

        score = compute_deal_score(100, 80)
        assert score > 50

    def test_overvalued(self) -> None:
        from app.helpers import compute_deal_score

        score = compute_deal_score(100, 120)
        assert score < 50

    def test_clamped_min(self) -> None:
        from app.helpers import compute_deal_score

        score = compute_deal_score(100, 1000)
        assert score >= 0

    def test_clamped_max(self) -> None:
        from app.helpers import compute_deal_score

        score = compute_deal_score(100, 0)
        assert score <= 100


class TestEnsemblePrediction:
    """Tests for ensemble prediction logic."""

    def test_no_models_returns_none(self) -> None:
        from app.helpers import ensemble_prediction

        input_df = pd.DataFrame({"feature": [1]})
        mean_pred, _spread, color = ensemble_prediction({}, input_df, None)
        assert mean_pred is None
        assert color == "red"


class TestShapLiteApproximation:
    """Tests for SHAP-lite approximation."""

    def test_linear_model(self) -> None:
        from sklearn.linear_model import LinearRegression

        from app.helpers import shap_lite_approximation

        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([1, 2, 3])
        model = LinearRegression().fit(X, y)

        class MockPreprocessor:
            def transform(self, X):
                return np.array([[1, 2]])

        result = shap_lite_approximation(model, pd.DataFrame({"a": [1]}), MockPreprocessor(), ["feat1", "feat2"])
        assert len(result) <= 8
        assert all(isinstance(item, tuple) for item in result)


class TestGenerateNaturalLanguageExplanation:
    """Tests for natural language price explanation."""

    def test_no_contributions(self) -> None:
        from app.helpers import generate_natural_language_explanation

        result = generate_natural_language_explanation([], 100, 100)
        assert "₹" in result

    def test_with_positive_contributions(self) -> None:
        from app.helpers import generate_natural_language_explanation

        contribs = [("year", 50000), ("brand", 30000)]
        result = generate_natural_language_explanation(contribs, 100000, 180000)
        assert "adds" in result

    def test_with_negative_contributions(self) -> None:
        from app.helpers import generate_natural_language_explanation

        contribs = [("kms_driven", -20000), ("age", -10000)]
        result = generate_natural_language_explanation(contribs, 100000, 70000)
        assert "reduces" in result


# ── Auth DB ─────────────────────────────────────────────────────────────────


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self) -> None:
        from app.auth_db import hash_password

        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert len(hashed) > 20

    def test_verify_correct_password(self) -> None:
        from app.auth_db import hash_password, verify_password

        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed)

    def test_verify_wrong_password(self) -> None:
        from app.auth_db import hash_password, verify_password

        hashed = hash_password("mypassword")
        assert not verify_password("wrongpassword", hashed)

    def test_verify_invalid_hash(self) -> None:
        from app.auth_db import verify_password

        assert not verify_password("password", "invalid-hash")


class TestUserHelpers:
    """Tests for user lookup helpers."""

    def test_username_exists(self) -> None:
        from app.auth_db import username_exists

        db = {"users": {"u1": {"username": "alice"}}}
        assert username_exists(db, "alice")
        assert username_exists(db, "Alice")  # case-insensitive
        assert not username_exists(db, "bob")

    def test_email_exists(self) -> None:
        from app.auth_db import email_exists

        db = {"users": {"u1": {"email": "alice@test.com"}}}
        assert email_exists(db, "alice@test.com")
        assert email_exists(db, "ALICE@TEST.COM")
        assert not email_exists(db, "bob@test.com")

    def test_get_user_by_username(self) -> None:
        from app.auth_db import get_user_by_username

        db = {"users": {"u1": {"username": "alice", "email": "alice@test.com"}}}
        user = get_user_by_username(db, "alice")
        assert user is not None
        assert user["email"] == "alice@test.com"

    def test_get_user_not_found(self) -> None:
        from app.auth_db import get_user_by_username

        db = {"users": {}}
        assert get_user_by_username(db, "alice") is None
