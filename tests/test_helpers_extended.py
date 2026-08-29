"""Tests for helpers.py — extended coverage for untested functions."""
import numpy as np
import pandas as pd
import pytest

from app.helpers import (
    ensemble_prediction,
    generate_data_quality_report,
    generate_natural_language_explanation,
    get_car_name_options,
    get_filtered_data,
    make_prediction,
    shap_lite_approximation,
)

# ─── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def sample_df():
    """Sample car DataFrame for testing."""
    return pd.DataFrame({
        "company": ["Maruti", "Maruti", "Hyundai", "Hyundai", "Honda"],
        "name": ["Swift", "Alto", "i20", "Creta", "City"],
        "year": [2020, 2018, 2021, 2022, 2019],
        "Price": [500000, 300000, 800000, 1200000, 700000],
        "kms_driven": [10000, 30000, 5000, 2000, 15000],
        "fuel_type": ["Petrol", "Petrol", "Diesel", "Diesel", "Petrol"],
    })


@pytest.fixture
def mock_model():
    """Mock model that returns fixed predictions."""
    class MockModel:
        def predict(self, X):
            return np.array([13.0])  # log(442413) ≈ 13.0
    return MockModel()


@pytest.fixture
def mock_preprocessor():
    """Mock preprocessor that passes through data."""
    class MockPreprocessor:
        def transform(self, X):
            return X.values
    return MockPreprocessor()


# ─── get_car_name_options ───────────────────────────────────────────


class TestGetCarNameOptions:
    """Tests for get_car_name_options function."""

    def test_returns_sorted_names(self, sample_df):
        result = get_car_name_options(sample_df, "Maruti")
        assert result == ["Alto", "Swift"]

    def test_returns_empty_for_unknown_company(self, sample_df):
        result = get_car_name_options(sample_df, "Toyota")
        assert result == []

    def test_single_car_company(self, sample_df):
        result = get_car_name_options(sample_df, "Honda")
        assert result == ["City"]

    def test_returns_list_type(self, sample_df):
        result = get_car_name_options(sample_df, "Hyundai")
        assert isinstance(result, list)


# ─── get_filtered_data ──────────────────────────────────────────────


class TestGetFilteredData:
    """Tests for get_filtered_data function."""

    def test_filters_by_company(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti"],
            fuels=["Petrol", "Diesel"],
            year_r=None,
            price_r=None,
            kms_r=None,
        )
        assert len(result) == 2
        assert all(result["company"] == "Maruti")

    def test_filters_by_fuel_type(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti", "Hyundai", "Honda"],
            fuels=["Diesel"],
            year_r=None,
            price_r=None,
            kms_r=None,
        )
        assert len(result) == 2
        assert all(result["fuel_type"] == "Diesel")

    def test_filters_by_year_range(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti", "Hyundai", "Honda"],
            fuels=["Petrol", "Diesel"],
            year_r=(2020, 2022),
            price_r=None,
            kms_r=None,
        )
        assert len(result) == 3
        assert all(result["year"] >= 2020)

    def test_filters_by_price_range(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti", "Hyundai", "Honda"],
            fuels=["Petrol", "Diesel"],
            year_r=None,
            price_r=(400000, 900000),
            kms_r=None,
        )
        assert len(result) == 3
        assert all(result["Price"] >= 400000)
        assert all(result["Price"] <= 900000)

    def test_filters_by_kms_range(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti", "Hyundai", "Honda"],
            fuels=["Petrol", "Diesel"],
            year_r=None,
            price_r=None,
            kms_r=(5000, 20000),
        )
        assert len(result) == 3
        assert all(result["kms_driven"] >= 5000)
        assert all(result["kms_driven"] <= 20000)

    def test_returns_dataframe(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti"],
            fuels=["Petrol"],
            year_r=None,
            price_r=None,
            kms_r=None,
        )
        assert isinstance(result, pd.DataFrame)

    def test_no_filters_returns_all(self, sample_df):
        result = get_filtered_data(
            sample_df,
            companies=["Maruti", "Hyundai", "Honda"],
            fuels=["Petrol", "Diesel"],
            year_r=None,
            price_r=None,
            kms_r=None,
        )
        assert len(result) == 5


# ─── make_prediction ────────────────────────────────────────────────


class TestMakePrediction:
    """Tests for make_prediction function."""

    def test_returns_float(self, mock_model, mock_preprocessor):
        input_df = pd.DataFrame({"feature": [1]})
        result = make_prediction(mock_model, input_df, mock_preprocessor)
        assert isinstance(result, float)

    def test_inverts_log_transform(self, mock_model, mock_preprocessor):
        input_df = pd.DataFrame({"feature": [1]})
        result = make_prediction(mock_model, input_df, mock_preprocessor)
        # mock_model returns 13.0, expm1(13.0) ≈ 442413
        assert result == pytest.approx(442413, rel=1e-3)

    def test_positive_prediction(self, mock_model, mock_preprocessor):
        input_df = pd.DataFrame({"feature": [1]})
        result = make_prediction(mock_model, input_df, mock_preprocessor)
        assert result > 0


# ─── ensemble_prediction ────────────────────────────────────────────


class TestEnsemblePrediction:
    """Tests for ensemble_prediction function."""

    def test_returns_tuple(self, mock_preprocessor):
        input_df = pd.DataFrame({"feature": [1]})
        models = {}
        mean, spread, color = ensemble_prediction(models, input_df, mock_preprocessor)
        assert mean is None
        assert spread is None
        assert color == "red"

    def test_with_models(self, mock_preprocessor):
        class MockModel:
            def predict(self, X):
                return np.array([13.0])

        input_df = pd.DataFrame({"feature": [1]})
        models = {
            "Linear Regression": MockModel(),
            "XGBoost": MockModel(),
            "Gradient Boosting": MockModel(),
        }
        mean, spread, color = ensemble_prediction(models, input_df, mock_preprocessor)
        assert mean is not None
        assert spread is not None
        assert color == "green"  # all same predictions = 0% spread

    def test_spread_color_coding(self, mock_preprocessor):
        class FastModel:
            def predict(self, X):
                return np.array([13.0])

        class SlowModel:
            def predict(self, X):
                return np.array([15.0])  # big difference

        input_df = pd.DataFrame({"feature": [1]})
        models = {
            "Linear Regression": FastModel(),
            "XGBoost": SlowModel(),
        }
        mean, spread, color = ensemble_prediction(models, input_df, mock_preprocessor)
        assert color == "red"  # spread > 20%


# ─── shap_lite_approximation ────────────────────────────────────────


class TestShapLiteApproximation:
    """Tests for shap_lite_approximation function."""

    def test_with_linear_model(self, mock_preprocessor):
        class LinearModel:
            coef_ = np.array([1.0, 2.0, 3.0])

        input_df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        feature_names = ["a", "b", "c"]
        result = shap_lite_approximation(LinearModel(), input_df, mock_preprocessor, feature_names)
        assert len(result) <= 8
        assert all(isinstance(item, tuple) for item in result)

    def test_with_tree_model(self, mock_preprocessor):
        class TreeModel:
            feature_importances_ = np.array([0.5, 0.3, 0.2])

        input_df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        feature_names = ["a", "b", "c"]
        result = shap_lite_approximation(TreeModel(), input_df, mock_preprocessor, feature_names)
        assert len(result) <= 8

    def test_returns_empty_for_unknown_model(self, mock_preprocessor):
        class UnknownModel:
            pass

        input_df = pd.DataFrame({"a": [1]})
        feature_names = ["a"]
        result = shap_lite_approximation(UnknownModel(), input_df, mock_preprocessor, feature_names)
        assert result == []


# ─── generate_data_quality_report ───────────────────────────────────


class TestGenerateDataQualityReport:
    """Tests for generate_data_quality_report function."""

    def test_returns_list_of_tuples(self):
        df = pd.DataFrame({
            "kms_driven": [1000, 2000, 3000],
            "fuel_type": ["Petrol", "Diesel", "Petrol"],
        })
        df_original = df.copy()
        result = generate_data_quality_report(df, df_original)
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) for item in result)
        assert len(result) == 4

    def test_counts_duplicates(self):
        df = pd.DataFrame({
            "kms_driven": [1000, 2000],
            "fuel_type": ["Petrol", "Diesel"],
        })
        df_original = pd.DataFrame({
            "kms_driven": [1000, 2000, 3000, 4000],
            "fuel_type": ["Petrol", "Diesel", "Petrol", "Diesel"],
        })
        result = generate_data_quality_report(df, df_original)
        # Should report 2 duplicates removed
        assert "2 duplicates removed" in result[1][1]

    def test_counts_alternative_fuels(self):
        df = pd.DataFrame({
            "kms_driven": [1000, 2000, 3000],
            "fuel_type": ["Petrol", "Diesel", "CNG"],
        })
        df_original = df.copy()
        result = generate_data_quality_report(df, df_original)
        # Should report 1 alternative fuel
        assert "1 rare fuel types" in result[3][1]


# ─── generate_natural_language_explanation ──────────────────────────


class TestGenerateNaturalLanguageExplanation:
    """Tests for generate_natural_language_explanation function."""

    def test_returns_string(self):
        result = generate_natural_language_explanation([], 500000, 600000)
        assert isinstance(result, str)

    def test_empty_contributions(self):
        result = generate_natural_language_explanation([], 500000, 600000)
        assert "This car is priced at" in result
        assert "." in result

    def test_with_positive_contributions(self):
        contributions = [("Year", 50000), ("Brand", 30000)]
        result = generate_natural_language_explanation(contributions, 500000, 600000)
        assert "Year" in result
        assert "Brand" in result
        assert "adds" in result

    def test_with_negative_contributions(self):
        contributions = [("Kms Driven", -20000), ("Age", -10000)]
        result = generate_natural_language_explanation(contributions, 500000, 450000)
        assert "Kms Driven" in result
        assert "reduces" in result

    def test_mixed_contributions(self):
        contributions = [("Year", 50000), ("Kms Driven", -20000)]
        result = generate_natural_language_explanation(contributions, 500000, 550000)
        assert "because" in result
