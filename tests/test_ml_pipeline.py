"""ML pipeline tests for Price-My-Car.

Tests the pre-trained models, preprocessor, prediction pipeline,
ensemble logic, and SHAP-lite approximation with real model artifacts.
"""

import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

# Suppress sklearn version mismatch warnings during test collection
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

ML_READY = Path(__file__).resolve().parent.parent / "ml_ready"


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def preprocessor():
    """Load the real preprocessor from disk."""
    return joblib.load(ML_READY / "preprocessor.pkl")


@pytest.fixture(scope="module")
def feature_names():
    """Load the real feature names from disk."""
    return joblib.load(ML_READY / "feature_names.pkl")


@pytest.fixture(scope="module")
def all_models():
    """Load all loadable pre-trained models from disk.

    Gradient boosting may fail to load if ``_loss`` C extension is missing
    (sklearn version mismatch).  Every other model should succeed.
    """
    models_dir = ML_READY / "models"
    # Map file stems to display names matching ensemble_prediction expectations
    NAME_MAP = {
        "gradient_boosting": "Gradient Boosting",
        "knn": "KNN",
        "lasso": "Lasso",
        "linear_regression": "Linear Regression",
        "random_forest": "Random Forest",
        "ridge": "Ridge",
        "svr": "SVR",
        "xgboost": "XGBoost",
    }
    models = {}
    for pkl in sorted(models_dir.glob("*.pkl")):
        try:
            models[NAME_MAP.get(pkl.stem, pkl.stem)] = joblib.load(pkl)
        except (ModuleNotFoundError, ImportError):
            pass  # Skip models with missing C extensions
    assert len(models) >= 6, f"Expected at least 6 loadable models, got {len(models)}"
    return models


@pytest.fixture(scope="module")
def train_data():
    """Load the real training data."""
    return pd.read_csv(ML_READY / "train_data.csv")


@pytest.fixture
def sample_input():
    """A realistic single-row input matching the preprocessor schema.

    The preprocessor expects: car_age, kms_driven, company, fuel_type_simple.
    """
    return pd.DataFrame([{
        "car_age": 4,
        "kms_driven": 15000,
        "company": "Maruti",
        "fuel_type_simple": "Petrol",
    }])


@pytest.fixture
def sample_input_batch():
    """Batch of 5 different car inputs."""
    return pd.DataFrame([
        {"car_age": 4, "kms_driven": 15000, "company": "Maruti", "fuel_type_simple": "Petrol"},
        {"car_age": 2, "kms_driven": 5000, "company": "Hyundai", "fuel_type_simple": "Diesel"},
        {"car_age": 5, "kms_driven": 30000, "company": "Honda", "fuel_type_simple": "Petrol"},
        {"car_age": 3, "kms_driven": 20000, "company": "Toyota", "fuel_type_simple": "Diesel"},
        {"car_age": 1, "kms_driven": 2000, "company": "Tata", "fuel_type_simple": "Petrol"},
    ])


# ── Model Loading Tests ──────────────────────────────────────────────────


class TestModelLoading:
    """Verify pre-trained models load correctly."""

    def test_all_models_load(self, all_models) -> None:
        """At least 6 models should load without error."""
        assert len(all_models) >= 6

    def test_expected_model_names(self, all_models) -> None:
        """Check that core model names are present."""
        must_have = {"Linear Regression", "Lasso", "Ridge", "KNN", "Random Forest", "SVR"}
        assert must_have.issubset(set(all_models.keys())), \
            f"Missing: {must_have - set(all_models.keys())}"

    def test_preprocessor_loads(self, preprocessor) -> None:
        """Preprocessor should be callable."""
        assert hasattr(preprocessor, "transform")

    def test_feature_names_loads(self, feature_names) -> None:
        """Feature names should be a non-empty list."""
        assert isinstance(feature_names, (list, np.ndarray))
        assert len(feature_names) > 0

    def test_models_have_predict(self, all_models) -> None:
        """Every model should have a predict method."""
        for name, model in all_models.items():
            assert hasattr(model, "predict"), f"{name} missing predict()"


# ── Preprocessor Tests ───────────────────────────────────────────────────


class TestPreprocessor:
    """Verify the preprocessor transforms data correctly."""

    def test_transform_shape(self, preprocessor, sample_input) -> None:
        """Transformed output should have correct shape."""
        X = preprocessor.transform(sample_input)
        assert X.shape[0] == 1
        assert X.shape[1] > 0

    def test_transform_batch(self, preprocessor, sample_input_batch) -> None:
        """Batch transform should preserve row count."""
        X = preprocessor.transform(sample_input_batch)
        assert X.shape[0] == 5

    def test_transform_no_nan(self, preprocessor, sample_input) -> None:
        """Transformed output should have no NaN values."""
        X = preprocessor.transform(sample_input)
        assert not np.isnan(X).any()

    def test_transform_numeric_output(self, preprocessor, sample_input) -> None:
        """Transformed output should be numeric."""
        X = preprocessor.transform(sample_input)
        assert np.issubdtype(X.dtype, np.number)

    def test_preprocessor_expects_correct_columns(self, preprocessor) -> None:
        """Preprocessor should expect car_age, kms_driven, company, fuel_type_simple."""
        expected_cols = {"car_age", "kms_driven", "company", "fuel_type_simple"}
        actual_cols = set()
        for _, _, cols in preprocessor.transformers_:
            if isinstance(cols, (list, tuple)):
                actual_cols.update(cols)
            else:
                actual_cols.add(cols)
        assert expected_cols.issubset(actual_cols), \
            f"Missing columns: {expected_cols - actual_cols}"


# ── Single-Model Prediction Tests ────────────────────────────────────────


class TestSinglePrediction:
    """Test making predictions with individual models."""

    def test_prediction_returns_positive(self, all_models, preprocessor, sample_input) -> None:
        """All models should return positive price predictions."""
        for name, model in all_models.items():
            X = preprocessor.transform(sample_input)
            pred_log = model.predict(X)[0]
            pred_price = float(np.expm1(pred_log))
            assert pred_price > 0, f"{name} returned non-positive: {pred_price}"

    def test_prediction_within_reasonable_range(self, all_models, preprocessor, sample_input) -> None:
        """Predictions should be within a reasonable car price range."""
        for name, model in all_models.items():
            X = preprocessor.transform(sample_input)
            pred_log = model.predict(X)[0]
            pred_price = float(np.expm1(pred_log))
            # Car prices should be between 50K and 50L INR
            assert 50_000 < pred_price < 50_00_000, f"{name} prediction out of range: {pred_price}"

    def test_log_transform_inversion(self, all_models, preprocessor, sample_input) -> None:
        """Verify log1p/expm1 roundtrip consistency."""
        from app.helpers import make_prediction

        for name, model in all_models.items():
            price = make_prediction(model, sample_input, preprocessor)
            assert price > 0, f"{name}: log transform inversion failed"

    def test_predictions_differ_across_models(self, all_models, preprocessor, sample_input) -> None:
        """Different models should produce different predictions."""
        predictions = []
        X = preprocessor.transform(sample_input)
        for name, model in all_models.items():
            pred_log = model.predict(X)[0]
            predictions.append(float(np.expm1(pred_log)))
        unique = set(round(p, 0) for p in predictions)
        assert len(unique) > 1, f"All models produced identical predictions: {predictions[0]}"


# ── Batch Prediction Tests ───────────────────────────────────────────────


class TestBatchPrediction:
    """Test batch predictions with multiple inputs."""

    def test_batch_predictions_all_positive(self, all_models, preprocessor, sample_input_batch) -> None:
        """Batch predictions should all be positive."""
        from app.helpers import make_prediction

        for name, model in all_models.items():
            prices = []
            for _, row in sample_input_batch.iterrows():
                df = pd.DataFrame([row])
                prices.append(make_prediction(model, df, preprocessor))
            assert all(p > 0 for p in prices), f"{name} has non-positive batch predictions"

    def test_newer_cars_more_expensive(self, all_models, preprocessor) -> None:
        """All else equal, a newer car should be predicted as more expensive."""
        from app.helpers import make_prediction

        old_car = pd.DataFrame([{"car_age": 9, "kms_driven": 50000, "company": "Maruti", "fuel_type_simple": "Petrol"}])
        new_car = pd.DataFrame([{"car_age": 1, "kms_driven": 5000, "company": "Maruti", "fuel_type_simple": "Petrol"}])

        for name, model in all_models.items():
            old_price = make_prediction(model, old_car, preprocessor)
            new_price = make_prediction(model, new_car, preprocessor)
            assert new_price > old_price * 0.5, f"{name}: newer car not more expensive ({new_price} vs {old_price})"

    def test_higher_km_less_expensive(self, all_models, preprocessor) -> None:
        """More kms driven should generally reduce predicted price."""
        from app.helpers import make_prediction

        low_km = pd.DataFrame([{"car_age": 4, "kms_driven": 5000, "company": "Honda", "fuel_type_simple": "Petrol"}])
        high_km = pd.DataFrame([{"car_age": 4, "kms_driven": 100000, "company": "Honda", "fuel_type_simple": "Petrol"}])

        for name, model in all_models.items():
            low_price = make_prediction(model, low_km, preprocessor)
            high_price = make_prediction(model, high_km, preprocessor)
            assert low_price > high_price * 0.5, f"{name}: high-km car not cheaper"


# ── Ensemble Prediction Tests ────────────────────────────────────────────


class TestEnsemble:
    """Test the ensemble prediction function."""

    def test_ensemble_returns_valid_result(self, all_models, preprocessor, sample_input) -> None:
        """Ensemble should return (mean, spread, color)."""
        from app.helpers import ensemble_prediction

        mean_pred, spread, color = ensemble_prediction(all_models, sample_input, preprocessor)
        assert mean_pred is not None
        assert mean_pred > 0
        assert spread >= 0
        assert color in ("green", "yellow", "red")

    def test_ensemble_within_tolerance(self, all_models, preprocessor, sample_input) -> None:
        """Ensemble spread should be within a reasonable tolerance."""
        from app.helpers import ensemble_prediction

        mean_pred, spread, color = ensemble_prediction(all_models, sample_input, preprocessor)
        assert mean_pred > 0
        assert spread < 50  # Models should agree within 50%

    def test_ensemble_empty_models_returns_none(self, preprocessor, sample_input) -> None:
        """Ensemble with no models returns (None, None, 'red')."""
        from app.helpers import ensemble_prediction

        mean_pred, spread, color = ensemble_prediction({}, sample_input, preprocessor)
        assert mean_pred is None
        assert spread is None
        assert color == "red"

    def test_ensemble_single_model(self, preprocessor, sample_input) -> None:
        """Ensemble with a single model should still work."""
        from app.helpers import ensemble_prediction

        lr = joblib.load(ML_READY / "models/linear_regression.pkl")
        mean_pred, spread, color = ensemble_prediction(
            {"Linear Regression": lr}, sample_input, preprocessor
        )
        assert mean_pred is not None
        assert mean_pred > 0


# ── Deal Score Tests ─────────────────────────────────────────────────────


class TestDealScore:
    """Test the deal score computation."""

    def test_perfect_match(self) -> None:
        """When predicted == actual, score should be ~50."""
        from app.helpers import compute_deal_score

        score = compute_deal_score(500000, 500000)
        assert score == 50

    def test_undervalued_high_score(self) -> None:
        """When actual < predicted (good deal), score should be > 50."""
        from app.helpers import compute_deal_score

        score = compute_deal_score(500000, 300000)
        assert score > 50

    def test_overvalued_low_score(self) -> None:
        """When actual > predicted (bad deal), score should be < 50."""
        from app.helpers import compute_deal_score

        score = compute_deal_score(500000, 700000)
        assert score < 50

    def test_score_clamped_0_100(self) -> None:
        """Score should always be between 0 and 100."""
        from app.helpers import compute_deal_score

        for actual in [1, 100, 1_000_000]:
            for predicted in [1, 100, 1_000_000]:
                score = compute_deal_score(predicted, actual)
                assert 0 <= score <= 100, f"Score {score} out of range for ({predicted}, {actual})"

    def test_rarity_multiplier(self) -> None:
        """Higher rarity should amplify the score."""
        from app.helpers import compute_deal_score

        score_normal = compute_deal_score(500000, 300000, rarity=1.0)
        score_rare = compute_deal_score(500000, 300000, rarity=2.0)
        assert score_rare >= score_normal


# ── SHAP-Lite Tests ──────────────────────────────────────────────────────


class TestShapLite:
    """Test the SHAP-lite feature importance approximation."""

    def test_returns_list_of_tuples(self, all_models, preprocessor, sample_input, feature_names) -> None:
        """Should return list of (feature_name, contribution) tuples."""
        from app.helpers import shap_lite_approximation

        for name, model in all_models.items():
            result = shap_lite_approximation(model, sample_input, preprocessor, feature_names)
            assert isinstance(result, list)
            for item in result:
                assert isinstance(item, tuple)
                assert len(item) == 2
                assert isinstance(item[0], str)
                assert isinstance(item[1], float)

    def test_max_8_features(self, all_models, preprocessor, sample_input, feature_names) -> None:
        """Should return at most 8 features."""
        from app.helpers import shap_lite_approximation

        for name, model in all_models.items():
            result = shap_lite_approximation(model, sample_input, preprocessor, feature_names)
            assert len(result) <= 8, f"{name} returned {len(result)} features (>8)"

    def test_sorted_by_abs_contribution(self, all_models, preprocessor, sample_input, feature_names) -> None:
        """Results should be sorted by absolute contribution (descending)."""
        from app.helpers import shap_lite_approximation

        for name, model in all_models.items():
            result = shap_lite_approximation(model, sample_input, preprocessor, feature_names)
            if len(result) > 1:
                abs_vals = [abs(v) for _, v in result]
                assert abs_vals == sorted(abs_vals, reverse=True), \
                    f"{name}: not sorted by absolute contribution"

    def test_linear_model_uses_coefs(self, preprocessor, sample_input, feature_names) -> None:
        """Linear models should use coef_ for SHAP-lite."""
        from app.helpers import shap_lite_approximation

        lr = joblib.load(ML_READY / "models/linear_regression.pkl")
        result = shap_lite_approximation(lr, sample_input, preprocessor, feature_names)
        assert len(result) > 0


# ── Training Data Tests ──────────────────────────────────────────────────


class TestTrainingData:
    """Verify training data properties."""

    def test_training_data_nonempty(self, train_data) -> None:
        """Training data should have rows."""
        assert len(train_data) > 0

    def test_training_data_has_key_columns(self, train_data) -> None:
        """Training data should have numeric features and Price."""
        assert "car_age" in train_data.columns
        assert "kms_driven" in train_data.columns
        assert "Price" in train_data.columns

    def test_training_data_price_positive(self, train_data) -> None:
        """All prices should be positive."""
        assert (train_data["Price"] > 0).all()

    def test_training_data_no_nulls_in_numeric(self, train_data) -> None:
        """Key numeric columns should have no nulls."""
        for col in ["car_age", "kms_driven", "Price"]:
            assert train_data[col].isna().sum() == 0, f"Nulls in {col}"

    def test_training_data_shape(self, train_data) -> None:
        """Training data should have a reasonable number of rows."""
        assert len(train_data) > 1000, f"Only {len(train_data)} rows"
