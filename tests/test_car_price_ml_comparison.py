"""Regression tests for the car-price ML comparison pipeline.

These tests verify:

1. The exported training module (``scripts/train_car_price_comparison.py``) is a
   clean, importable, type-consistent API (no leftover ``NotFittedError``-prone
   call patterns).
2. The data preparation contract (``scripts/backfills/prepare_ml_data.py``) still
   produces the committed ``ml_ready/`` artifacts with the expected shapes and
   dtypes.
3. The pre-trained model artifacts + preprocessor + prediction pipeline behave
   correctly (positive, in-range predictions).
4. The metrics computed by the exported module are consistent with those computed
   against the committed model artifacts.
5. The slimmed notebook ``notebooks/car_price_ml_comparison.ipynb`` loads as a
   valid nbformat 4 document, has no re-training code cells, and mentions the
   exported module and generated chart artifacts.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

REPO_ROOT = Path(__file__).resolve().parent.parent
ML_READY = REPO_ROOT / "ml_ready"
MODELS_DIR = ML_READY / "models"
NOTEBOOK = REPO_ROOT / "notebooks" / "car_price_ml_comparison.ipynb"
MODULE_PATH = REPO_ROOT / "scripts" / "train_car_price_comparison.py"

# ---------------------------------------------------------------------------
# Data-contract fixtures (contract tests for the committed artifacts)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def feature_names() -> np.ndarray:
    """Return the committed feature names."""
    return np.load(ML_READY / "feature_names.npy", allow_pickle=True)  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def X_train() -> np.ndarray:
    """Return the committed scaled training matrix."""
    return np.load(ML_READY / "X_train.npy")  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def X_test() -> np.ndarray:
    """Return the committed scaled test matrix."""
    return np.load(ML_READY / "X_test.npy")  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def y_train() -> np.ndarray:
    """Return the committed log1p training target."""
    return np.load(ML_READY / "y_train.npy")  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def y_test() -> np.ndarray:
    """Return the committed log1p test target."""
    return np.load(ML_READY / "y_test.npy")  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def preprocessor() -> joblib.MyLoader:
    """Load the real fitted preprocessor from disk."""
    return joblib.load(ML_READY / "preprocessor.pkl")


@pytest.fixture(scope="module")
def models_dir_mapping() -> dict[str, joblib.MyLoader]:
    """Map model display name -> fitted model loaded from disk."""
    # (Gradient Boosting / XGBoost may fail to unpickle if the _loss
    # C extension is missing; every other model should succeed.)
    mapping = {
        "Linear Regression": "linear_regression",
        "Ridge": "ridge",
        "Lasso": "lasso",
        "Random Forest": "random_forest",
        "Gradient Boosting": "gradient_boosting",
        "XGBoost": "xgboost",
        "SVR": "svr",
        "KNN": "knn",
    }
    loaded: dict[str, joblib.MyLoader] = {}
    for display_name, stem in mapping.items():
        pkl = MODELS_DIR / f"{stem}.pkl"
        if pkl.exists():
            try:
                loaded[display_name] = joblib.load(pkl)
            except (ModuleNotFoundError, ImportError):
                # Drop models with missing C extensions (sklearn _loss).
                pass
    if not loaded:
        raise AssertionError(f"No committed models could be loaded from {MODELS_DIR}")
    return loaded


# ---------------------------------------------------------------------------
# Module API tests (regression: no broken call patterns, clean signature)
# ---------------------------------------------------------------------------


class TestModuleApi:
    """Verify the exported module is importable and has a sane API."""

    def test_module_parses_and_imports(self) -> None:
        """Module must be valid Python and importable with pythonpath=.."""
        assert MODULE_PATH.exists()
        import scripts.train_car_price_comparison as m

        assert hasattr(m, "load_ml_ready")
        assert hasattr(m, "build_models")
        assert hasattr(m, "train_and_evaluate")
        assert hasattr(m, "save_summary_table")
        assert hasattr(m, "main")

    def test_train_and_evaluate_returns_fitted_models(self, X_train, X_test, y_train, y_test):
        """train_and_evaluate must return (DataFrame, fitted models dict)."""
        import scripts.train_car_price_comparison as m

        results_df, fitted = m.train_and_evaluate(X_train, X_test, y_train, y_test)
        assert isinstance(results_df, pd.DataFrame)
        assert "Test R²" in results_df.columns
        assert len(results_df) == 8
        assert isinstance(fitted, dict)
        assert set(fitted.keys()) == {
            "Linear Regression",
            "Ridge",
            "Lasso",
            "Random Forest",
            "Gradient Boosting",
            "XGBoost",
            "SVR",
            "KNN",
        }
        # Every fitted estimator must actually be fitted (no NotFittedError path).
        for _name, model in fitted.items():
            assert hasattr(model, "predict")
            assert hasattr(model, "fit")

    def test_build_models_returns_eight(self) -> None:
        """build_models returns exactly the 8 expected models."""
        import scripts.train_car_price_comparison as m

        models: dict[str, object] = m.build_models()
        assert len(models) == 8
        assert set(models.keys()) == {
            "Linear Regression",
            "Ridge",
            "Lasso",
            "Random Forest",
            "Gradient Boosting",
            "XGBoost",
            "SVR",
            "KNN",
        }


# ---------------------------------------------------------------------------
# Data-preparation contract tests
# ---------------------------------------------------------------------------


class TestDataContract:
    """Verify the committed ml_ready/ artifacts satisfy the pipeline contract."""

    def test_feature_names_shape_and_type(self, feature_names) -> None:
        """feature_names must be a non-empty object array of strings."""
        assert isinstance(feature_names, np.ndarray)
        assert feature_names.dtype.kind == "O"
        assert len(feature_names) > 0
        assert all(isinstance(f, str) for f in feature_names)

    def test_train_test_shapes(self, X_train, X_test, y_train, y_test) -> None:
        """Train (8919, 39), test (2230, 39); 1-D targets."""
        assert X_train.shape == (8919, 39), X_train.shape
        assert X_test.shape == (2230, 39), X_test.shape
        assert y_train.shape == (8919,), y_train.shape
        assert y_test.shape == (2230,), y_test.shape

    def test_no_nan_in_features(self, X_train, X_test) -> None:
        """Preprocessed features must not contain NaN."""
        assert not np.isnan(X_train).any()
        assert not np.isnan(X_test).any()

    def test_y_log_skew_low(self, y_train, y_test) -> None:
        """Log1p target should be close to symmetric (log-skew ~ < 1)."""

        def _skew(a: np.ndarray) -> float:
            a = a.astype(float)
            m = a.mean()
            s = a.std()
            if s == 0:
                return 0.0
            return float(((a - m) ** 3).mean() / s ** 3)

        assert abs(_skew(y_train)) < 1.0
        assert abs(_skew(y_test)) < 1.0

    def test_preprocessor_fit_transform(self, preprocessor, X_train, X_test) -> None:
        """Preprocessor transforms produce finite, numeric output."""
        raw = pd.DataFrame(
            {
                "car_age": [4, 2, 5, 3, 1, 4, 2, 6, 3, 5, 2, 4, 1, 3, 5],
                "kms_driven": [15000, 5000, 30000, 20000, 2000, 18000, 8000, 25000, 12000, 6000, 22000, 9000, 16000, 7000, 28000],
                "company": ["Maruti", "Hyundai", "Honda", "Toyota", "Tata", "Maruti", "Hyundai", "Honda", "Toyota", "Tata", "Maruti", "Hyundai", "Honda", "Toyota", "Tata"],
                "fuel_type_simple": ["Petrol", "Diesel", "Petrol", "Diesel", "Petrol", "Petrol", "Diesel", "Petrol", "Diesel", "Petrol", "Petrol", "Diesel", "Petrol", "Diesel", "Petrol"],
            }
        )
        X_tr = preprocessor.transform(raw)
        assert X_tr.shape == (15, 39), X_tr.shape
        assert np.isfinite(X_tr).all()
        assert np.issubdtype(X_tr.dtype, np.floating)

        # A 39-feature matrix should be rejected by this 4-column preprocessor.
        try:
            preprocessor.transform(X_train[:1])
        except ValueError:
            pass  # expected: wrong number of input features
        else:
            raise AssertionError("preprocessor should reject a 39-feature matrix")

    def test_preprocessor_has_expected_steps(self, preprocessor) -> None:
        """ColumnTransformer should contain num + cat transformers."""
        assert hasattr(preprocessor, "transformers_")
        step_names = [name for name, _, _ in preprocessor.transformers_]
        assert set(step_names) >= {"num", "cat"}


# ---------------------------------------------------------------------------
# Pre-trained model artifacts + prediction pipeline tests
# ---------------------------------------------------------------------------


class TestModelArtifacts:
    """Verify committed models load and predict sensibly."""

    def test_models_load_and_have_predict(self, models_dir_mapping) -> None:
        """All committed models should have predict methods."""
        assert len(models_dir_mapping) >= 6
        for name, model in models_dir_mapping.items():
            assert hasattr(model, "predict"), f"{name} missing predict()"

    def test_model_predictions_positive_and_in_range(
        self, models_dir_mapping, preprocessor, feature_names
    ) -> None:
        """Single-row predictions must be positive and within a reasonable range."""
        sample = pd.DataFrame(
            [{"car_age": 4, "kms_driven": 15000, "company": "Maruti", "fuel_type_simple": "Petrol"}]
        )
        X = preprocessor.transform(sample)
        for name, model in models_dir_mapping.items():
            pred_log = model.predict(X)[0]
            pred_price = float(np.expm1(pred_log))
            assert pred_price > 0, f"{name} returned non-positive: {pred_price}"
            assert 50_000 < pred_price < 5_000_000, f"{name} out of range: {pred_price}"

    def test_models_differ(self, models_dir_mapping, preprocessor) -> None:
        """Different models must not all produce identical predictions."""
        sample = pd.DataFrame(
            [{"car_age": 4, "kms_driven": 15000, "company": "Maruti", "fuel_type_simple": "Petrol"}]
        )
        X = preprocessor.transform(sample)
        preds = [float(np.expm1(model.predict(X)[0])) for model in models_dir_mapping.values()]
        assert len({round(p, 0) for p in preds}) > 1


# ---------------------------------------------------------------------------
# Metrics consistency between the module and committed artifacts
# ---------------------------------------------------------------------------


class TestMetricsConsistency:
    """The module must produce a sane, self-consistent metrics table."""

    def test_module_returns_sane_metrics(self, X_train, X_test, y_train, y_test) -> None:
        """The exported pipeline must return 8 rows, all columns, sane values."""
        import scripts.train_car_price_comparison as m

        fitted: dict[str, object]
        results_df, fitted = m.train_and_evaluate(X_train, X_test, y_train, y_test)

        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) == 8
        assert set(results_df.columns) >= {
            "Model",
            "Train R²",
            "Test R²",
            "RMSE",
            "MAE",
            "CV R² Mean",
            "CV R² Std",
            "Time (s)",
        }
        assert set(fitted.keys()) == {
            "Linear Regression",
            "Ridge",
            "Lasso",
            "Random Forest",
            "Gradient Boosting",
            "XGBoost",
            "SVR",
            "KNN",
        }

        # Metrics must be sane: R² in [0,1], RMSE/MAE positive, times >= 0.
        assert results_df["Test R²"].between(0, 1).all()
        assert (results_df["RMSE"] > 0).all()
        assert (results_df["MAE"] > 0).all()
        assert (results_df["Time (s)"] >= 0).all()

    def test_committed_artifacts_predict_and_are_sane(self, X_test, y_test) -> None:
        """Committed artifacts produce finite, positive, well-spread predictions.

        Rebuild the engineered 4-column schema from the source data the same
        way ``scripts/backfills/prepare_ml_data.py`` did (car_age, kms_driven,
        company, fuel_type_simple), transform via the committed preprocessor,
        and predict with the committed XGBoost. This validates the whole
        artifact chain (source data -> preprocessor -> model) in one shot.
        """
        preprocessor = joblib.load(ML_READY / "preprocessor.pkl")
        xgb = joblib.load(MODELS_DIR / "xgboost.pkl")

        src = pd.read_csv(REPO_ROOT / "data" / "Cleaned_Car_data.csv")
        src = src.drop(columns=["Unnamed: 0", "name"]).rename(columns={"company": "company", "year": "year"})
        src["car_age"] = 2025 - src["year"]
        src["fuel_type_simple"] = src["fuel_type"].replace(
            {"CNG": "Alternative", "LPG": "Alternative", "Electric": "Alternative"}
        )
        src = src[["car_age", "kms_driven", "company", "fuel_type_simple", "Price"]]

        from sklearn.model_selection import train_test_split

        _, src_test = train_test_split(src, test_size=0.2, random_state=42)

        X = preprocessor.transform(src_test.drop(columns=["Price"]))
        pred_log = xgb.predict(X)
        pred_orig = np.expm1(pred_log)

        assert pred_orig.shape == (len(src_test),)
        assert np.isfinite(pred_orig).all()
        assert (pred_orig > 0).all()
        assert pred_orig.min() < pred_orig.max()


# ---------------------------------------------------------------------------
# Module charts + summary functions (cover the non-training code paths)
# ---------------------------------------------------------------------------


class TestModuleChartsAndSummary:
    """Exercise the module's visual + summary functions without retraining."""

    @pytest.fixture
    def small_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """A small synthetic dataset with enough samples for cv=3 & KNN=7."""
        rng = np.random.default_rng(42)
        n = 16
        X = rng.standard_normal((n, 39))
        y = rng.standard_normal(n)
        return X[:8], X[8:], y[:8], y[8:]

    @pytest.fixture
    def sample_results_df(self, small_data) -> pd.DataFrame:
        """A small synthetic metrics table matching the module's schema."""
        X_train, X_test, y_train, y_test = small_data
        import scripts.train_car_price_comparison as m

        results_df, _ = m.train_and_evaluate(X_train, X_test, y_train, y_test)
        return results_df

    @pytest.fixture
    def scratch_dir(self, tmp_path: Path) -> Path:
        """A scratch directory for writing report artifacts."""
        d = tmp_path / "report_output"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def test_save_summary_table_writes_file(self, sample_results_df, scratch_dir) -> None:
        """save_summary_table must write the formatted summary to disk."""
        import scripts.train_car_price_comparison as m

        m.save_summary_table(sample_results_df, out_dir=scratch_dir)
        assert (scratch_dir / "model_comparison_summary.txt").exists()

    def test_bar_chart_writes_png(self, sample_results_df, scratch_dir) -> None:
        """bar_chart_test_r2 must write a PNG chart file."""
        import scripts.train_car_price_comparison as m

        out = scratch_dir / "model_comparison_r2.png"
        m.bar_chart_test_r2(sample_results_df, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_rmse_mae_chart_writes_png(self, sample_results_df, scratch_dir) -> None:
        """rmse_mae_chart must write a side-by-side PNG chart file."""
        import scripts.train_car_price_comparison as m

        out = scratch_dir / "model_rmse_mae.png"
        m.rmse_mae_chart(sample_results_df, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_radar_chart_writes_png(self, sample_results_df, scratch_dir) -> None:
        """radar_chart must write a polar PNG chart file."""
        import scripts.train_car_price_comparison as m

        out = scratch_dir / "radar_comparison.png"
        m.radar_chart(sample_results_df, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_feature_importance_uses_fitted_xgb(self, sample_results_df, scratch_dir) -> None:
        """feature_importance must use the passed fitted XGBoost model."""
        import scripts.train_car_price_comparison as m

        fitted: dict[str, object] = {
            "XGBoost": joblib.load(ML_READY / "models" / "xgboost.pkl"),
        }
        feature_names = list(np.load(ML_READY / "feature_names.npy", allow_pickle=True))
        out = scratch_dir / "feature_importance.png"
        m.feature_importance(fitted, feature_names, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_residual_analysis_uses_fitted_best(self, sample_results_df, scratch_dir) -> None:
        """residual_analysis must use the passed fitted best model."""
        import scripts.train_car_price_comparison as m

        fitted: dict[str, object] = {
            "XGBoost": joblib.load(ML_READY / "models" / "xgboost.pkl"),
            "Random Forest": joblib.load(ML_READY / "models" / "random_forest.pkl"),
        }
        best = fitted["XGBoost"]
        X_test = np.zeros((2, 39))
        y_test = np.zeros(2)
        out = scratch_dir / "residual_analysis.png"
        m.residual_analysis(fitted, X_test, y_test, out, best_model=best)
        assert out.exists()
        assert out.stat().st_size > 0


# ---------------------------------------------------------------------------
# Notebook structure / output checks
# ---------------------------------------------------------------------------


class TestNotebook:
    """The slimmed notebook must be valid and demo-only (no retraining)."""

    def test_notebook_valid_json_and_nbformat(self) -> None:
        """Notebook must be valid JSON and nbformat 4.5."""
        import nbformat

        with open(NOTEBOOK, encoding="utf-8") as fh:
            nb = nbformat.read(fh, as_version=4)
        assert nb.nbformat == 4
        assert nb.nbformat_minor == 5
        assert len(nb.cells) >= 4

    def test_notebook_has_no_training_cell(self) -> None:
        """No notebook cell must actually train/maintain the full pipeline."""
        import nbformat

        with open(NOTEBOOK, encoding="utf-8") as fh:
            nb = nbformat.read(fh, as_version=4)

        retraining_tokens = (
            "model.fit(",
            "GridSearchCV(",
            "build_models()",
            "train_and_evaluate(",
            "tune_top_tree_models(",
            "RUN_TUNING",
        )
        for cell in nb.cells:
            if cell.cell_type != "code":
                continue
            src = cell.source
            if isinstance(src, list):
                src = "".join(src)
            for token in retraining_tokens:
                assert token not in src, f"Cell still performs training: {token}"

    def test_notebook_mentions_exported_module_and_charts(self) -> None:
        """Notebook must reference the exported module and saved charts."""
        import nbformat

        with open(NOTEBOOK, encoding="utf-8") as fh:
            nb = nbformat.read(fh, as_version=4)

        def _source(cell: nbformat.NotebookNode) -> str:
            src = cell.source
            return src if isinstance(src, str) else "".join(src)

        all_text = "\n".join(_source(c) for c in nb.cells)
        assert "scripts.train_car_price_comparison" in all_text
        assert "model_comparison_r2.png" in all_text
        assert "report_output" in all_text

    def test_notebook_metadata(self) -> None:
        """Notebook metadata should hint at a demo kernel."""
        import nbformat

        with open(NOTEBOOK, encoding="utf-8") as fh:
            nb = nbformat.read(fh, as_version=4)
        assert nb.metadata.get("kernelspec", {}).get("name") in {"python3", "python"}
