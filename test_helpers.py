"""
Unit tests for AutoIntel — Car Price Intelligence helper functions.
Tests all pure logic functions, data-dependent functions, and model-dependent functions.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from helpers import (
    fmt_inr, get_price_tier, price_tier_badge, get_fuel_simple,
    get_company_tier, compute_deal_score, get_car_name_options,
    get_filtered_data, generate_data_quality_report,
    generate_natural_language_explanation, make_prediction,
    shap_lite_approximation, ensemble_prediction, CURRENT_YEAR,
    MODEL_METRICS, METRICS_DF
)
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


# =============================================================================
# Tests for fmt_inr
# =============================================================================
class TestFmtInr:
    def test_basic_values(self):
        """Test basic INR formatting"""
        assert fmt_inr(0) == "₹0"
        assert fmt_inr(100) == "₹100"
        assert fmt_inr(999) == "₹999"
        assert fmt_inr(1000) == "₹1,000"
        assert fmt_inr(10000) == "₹10,000"
        assert fmt_inr(100000) == "₹1.0L"
        assert fmt_inr(500000) == "₹5.0L"

    def test_lakhs(self):
        """Test lakh formatting (>= 1e5)"""
        assert fmt_inr(100000) == "₹1.0L"
        assert fmt_inr(150000) == "₹1.5L"
        assert fmt_inr(1250000) == "₹12.5L"

    def test_crores(self):
        """Test crore formatting (>= 1e7)"""
        assert fmt_inr(10000000) == "₹1.00Cr"
        assert fmt_inr(15000000) == "₹1.50Cr"
        assert fmt_inr(100000000) == "₹10.00Cr"

    def test_edge_cases(self):
        """Test edge cases"""
        assert fmt_inr(-1000) == "₹-1,000"
        assert fmt_inr(99999) == "₹99,999"
        assert fmt_inr(100001) == "₹1.0L"


# =============================================================================
# Tests for get_price_tier
# =============================================================================
class TestGetPriceTier:
    def test_luxury(self):
        tier, cls = get_price_tier(2000000)
        assert tier == 'Luxury'
        assert cls == 'badge-luxury'

        tier, cls = get_price_tier(5000000)
        assert tier == 'Luxury'
        assert cls == 'badge-luxury'

    def test_premium(self):
        tier, cls = get_price_tier(800000)
        assert tier == 'Premium'
        assert cls == 'badge-premium'

        tier, cls = get_price_tier(1500000)
        assert tier == 'Premium'
        assert cls == 'badge-premium'

    def test_mid_range(self):
        tier, cls = get_price_tier(300000)
        assert tier == 'Mid-range'
        assert cls == 'badge-mid'

        tier, cls = get_price_tier(500000)
        assert tier == 'Mid-range'
        assert cls == 'badge-mid'

    def test_budget(self):
        tier, cls = get_price_tier(0)
        assert tier == 'Budget'
        assert cls == 'badge-budget'

        tier, cls = get_price_tier(100000)
        assert tier == 'Budget'
        assert cls == 'badge-budget'

    def test_boundary_conditions(self):
        tier, _ = get_price_tier(300000)
        assert tier == 'Mid-range'

        tier, _ = get_price_tier(800000)
        assert tier == 'Premium'

        tier, _ = get_price_tier(2000000)
        assert tier == 'Luxury'


# =============================================================================
# Tests for price_tier_badge
# =============================================================================
class TestPriceTierBadge:
    def test_returns_html_span(self):
        result = price_tier_badge(50000)
        assert '<span class=' in result
        assert 'badge-budget' in result
        assert 'Budget' in result

        result = price_tier_badge(3000000)
        assert 'badge-luxury' in result
        assert 'Luxury' in result

    def test_all_tiers(self):
        result = price_tier_badge(100000)
        assert 'badge-budget' in result

        result = price_tier_badge(500000)
        assert 'badge-mid' in result

        result = price_tier_badge(1000000)
        assert 'badge-premium' in result

        result = price_tier_badge(3000000)
        assert 'badge-luxury' in result


# =============================================================================
# Tests for get_fuel_simple
# =============================================================================
class TestGetFuelSimple:
    def test_petrol_diesel_unchanged(self):
        assert get_fuel_simple('Petrol') == 'Petrol'
        assert get_fuel_simple('Diesel') == 'Diesel'

    def test_alternative_fuels(self):
        assert get_fuel_simple('CNG') == 'Alternative'
        assert get_fuel_simple('LPG') == 'Alternative'
        assert get_fuel_simple('Electric') == 'Alternative'

    def test_case_sensitivity(self):
        assert get_fuel_simple('petrol') == 'petrol'


# =============================================================================
# Tests for get_company_tier
# =============================================================================
class TestGetCompanyTier:
    def test_luxury(self):
        assert get_company_tier(1500000) == 'Luxury'
        assert get_company_tier(3000000) == 'Luxury'

    def test_premium(self):
        assert get_company_tier(600000) == 'Premium'
        assert get_company_tier(1000000) == 'Premium'

    def test_mid(self):
        assert get_company_tier(300000) == 'Mid'
        assert get_company_tier(450000) == 'Mid'

    def test_budget(self):
        assert get_company_tier(0) == 'Budget'
        assert get_company_tier(100000) == 'Budget'


# =============================================================================
# Tests for compute_deal_score
# =============================================================================
class TestComputeDealScore:
    def test_excellent_deal(self):
        """When predicted > actual, car is underpriced = good deal"""
        score = compute_deal_score(100000, 50000)
        assert 50 <= score <= 100

    def test_bad_deal(self):
        """When predicted < actual, car is overpriced"""
        score = compute_deal_score(100000, 150000)
        assert 0 <= score <= 50

    def test_perfect_match(self):
        """When predicted == actual, score should be 50"""
        score = compute_deal_score(100000, 100000)
        assert score == 50

    def test_score_range(self):
        """Score should always be between 0 and 100"""
        for _ in range(100):
            pred = float(np.random.uniform(10000, 1000000))
            actual = float(np.random.uniform(10000, 1000000))
            score = compute_deal_score(pred, actual)
            assert 0 <= score <= 100, f"Score {score} out of range"

    def test_rarity_factor(self):
        """Rarity > 1.0 should boost score"""
        base_score = compute_deal_score(100000, 50000, rarity=1.0)
        boosted_score = compute_deal_score(100000, 50000, rarity=1.5)
        assert boosted_score >= base_score

    def test_rarity_below_one(self):
        """Rarity < 1.0 should reduce score"""
        base_score = compute_deal_score(100000, 50000, rarity=1.0)
        reduced_score = compute_deal_score(100000, 50000, rarity=0.5)
        assert reduced_score <= base_score


# =============================================================================
# Tests for get_car_name_options
# =============================================================================
class TestGetCarNameOptions:
    def setup_method(self):
        self.df = pd.DataFrame({
            'name': ['Swift VDI', 'Swift ZDI', 'Wagon R', 'Alto 800', 'i20 Magna'],
            'company': ['Maruti', 'Maruti', 'Maruti', 'Maruti', 'Hyundai'],
            'Price': [500000, 600000, 300000, 200000, 550000]
        })

    def test_returns_sorted_names(self):
        names = get_car_name_options(self.df, 'Maruti')
        assert names == ['Alto 800', 'Swift VDI', 'Swift ZDI', 'Wagon R']
        assert len(names) == 4

    def test_single_result(self):
        names = get_car_name_options(self.df, 'Hyundai')
        assert names == ['i20 Magna']

    def test_no_results(self):
        names = get_car_name_options(self.df, 'Toyota')
        assert names == []

    def test_empty_dataframe(self):
        empty_df = pd.DataFrame(columns=['name', 'company', 'Price'])
        names = get_car_name_options(empty_df, 'Maruti')
        assert names == []


# =============================================================================
# Tests for get_filtered_data
# =============================================================================
class TestGetFilteredData:
    def setup_method(self):
        self.df = pd.DataFrame({
            'name': ['Car A', 'Car B', 'Car C', 'Car D', 'Car E'],
            'company': ['Maruti', 'Hyundai', 'Maruti', 'Toyota', 'BMW'],
            'fuel_type': ['Petrol', 'Diesel', 'Petrol', 'Petrol', 'Diesel'],
            'year': [2018, 2019, 2020, 2015, 2021],
            'Price': [500000, 800000, 600000, 1200000, 3000000],
            'kms_driven': [30000, 50000, 20000, 80000, 10000],
            'car_age': [7, 6, 5, 10, 4]
        })

    def test_filter_by_company(self):
        result = get_filtered_data(self.df, ['Maruti'], ['Petrol', 'Diesel'],
                                    None, None, None)
        assert len(result) == 2
        assert all(result['company'] == 'Maruti')

    def test_filter_by_fuel(self):
        result = get_filtered_data(self.df, ['Maruti', 'Hyundai', 'Toyota', 'BMW'],
                                    ['Diesel'], None, None, None)
        assert len(result) == 2
        assert all(result['fuel_type'] == 'Diesel')

    def test_filter_by_year_range(self):
        result = get_filtered_data(self.df, ['Maruti', 'Hyundai', 'Toyota', 'BMW'],
                                    ['Petrol', 'Diesel'], (2019, 2021), None, None)
        assert len(result) == 3
        assert all(result['year'].between(2019, 2021))

    def test_filter_by_price_range(self):
        result = get_filtered_data(self.df, ['Maruti', 'Hyundai', 'Toyota', 'BMW'],
                                    ['Petrol', 'Diesel'], None, (500000, 1000000), None)
        assert len(result) == 3  # Car A (500K), Car B (800K), Car C (600K)
        assert all(result['Price'].between(500000, 1000000))

    def test_filter_by_kms_range(self):
        result = get_filtered_data(self.df, ['Maruti', 'Hyundai', 'Toyota', 'BMW'],
                                    ['Petrol', 'Diesel'], None, None, (0, 30000))
        assert len(result) == 3
        assert all(result['kms_driven'].between(0, 30000))

    def test_combined_filters(self):
        result = get_filtered_data(self.df, ['Maruti'], ['Petrol'],
                                    (2018, 2020), (400000, 700000), (10000, 40000))
        assert len(result) == 2

    def test_no_matches(self):
        result = get_filtered_data(self.df, ['Toyota'], ['Diesel'],
                                    None, None, None)
        assert len(result) == 0

    def test_empty_filters_returns_nothing(self):
        """Empty filter lists should return no rows (no match)"""
        result = get_filtered_data(self.df, [], [], None, None, None)
        assert len(result) == 0


# =============================================================================
# Tests for generate_data_quality_report
# =============================================================================
class TestGenerateDataQualityReport:
    def setup_method(self):
        self.df_clean = pd.DataFrame({
            'name': ['Car A', 'Car B', 'Car C'],
            'Price': [500000, 800000, 600000],
            'kms_driven': [30000, 50000, 20000],
            'fuel_type': ['Petrol', 'Diesel', 'CNG'],
            'year': [2018, 2019, 2020]
        })
        self.df_dupes = pd.DataFrame({
            'name': ['Car A', 'Car B', 'Car B', 'Car C', 'Car D'],
            'Price': [500000, 800000, 800000, 600000, 100000],
            'kms_driven': [30000, 50000, 50000, 20000, 40000],
            'fuel_type': ['Petrol', 'Diesel', 'Diesel', 'CNG', 'Petrol'],
            'year': [2018, 2019, 2019, 2020, 2021]
        })

    def test_no_duplicates(self):
        report = generate_data_quality_report(self.df_clean, self.df_clean)
        assert len(report) == 4
        assert any('0 duplicates' in item[1] for item in report)

    def test_duplicates_found(self):
        report = generate_data_quality_report(self.df_clean, self.df_dupes)
        assert any('2 duplicates' in item[1] for item in report)

    def test_no_nulls(self):
        report = generate_data_quality_report(self.df_clean, self.df_clean)
        assert any('No nulls' in item[1] for item in report)

    def test_alternative_fuels_detected(self):
        report = generate_data_quality_report(self.df_clean, self.df_clean)
        fuel_reports = [item[1] for item in report if 'Alternative' in item[1]]
        assert len(fuel_reports) > 0

    def test_returns_four_items(self):
        report = generate_data_quality_report(self.df_clean, self.df_clean)
        assert len(report) == 4


# =============================================================================
# Tests for generate_natural_language_explanation
# =============================================================================
class TestGenerateNaturalLanguageExplanation:
    def test_no_contributions(self):
        result = generate_natural_language_explanation([], 50000, 500000)
        assert 'This car is priced at' in result
        assert '₹' in result
        assert result.endswith('.')

    def test_with_positive_contributions(self):
        """Should mention price increases"""
        contribs = [('company_BMW', 200000), ('fuel_Petrol', 50000)]
        result = generate_natural_language_explanation(contribs, 200000, 450000)
        assert 'adds' in result
        assert 'company_BMW' in result

    def test_with_negative_contributions(self):
        """Should mention price reductions"""
        contribs = [('car_age', -50000), ('kms_driven', -30000)]
        result = generate_natural_language_explanation(contribs, 500000, 420000)
        assert 'reduces' in result
        assert 'car_age' in result

    def test_mixed_contributions(self):
        contribs = [('company_BMW', 200000), ('car_age', -50000), ('kms_driven', -30000)]
        result = generate_natural_language_explanation(contribs, 300000, 420000)
        assert 'adds' in result
        assert 'reduces' in result

    def test_limits_contributions(self):
        """Should only show top 3 positive and top 3 negative"""
        contribs = [
            ('A', 100), ('B', 90), ('C', 80), ('D', 70),
            ('E', -100), ('F', -90), ('G', -80), ('H', -70)
        ]
        result = generate_natural_language_explanation(contribs, 500000, 500000)
        for name in ['A', 'B', 'C']:
            assert name in result
        for name in ['E', 'F', 'G']:
            assert name in result
        # 'D' and 'H' should NOT be mentioned (outside top 3)
        assert 'D' not in result
        assert 'H' not in result


# =============================================================================
# Tests for make_prediction
# =============================================================================
class TestMakePrediction:
    def test_basic_prediction(self):
        """Should run model prediction and invert log-transform"""
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[0.5, 0.3]])

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([14.0])

        input_df = pd.DataFrame({'feature1': [0.5], 'feature2': [0.3]})
        result = make_prediction(mock_model, input_df, mock_preprocessor)

        expected = float(np.expm1(14.0))
        assert abs(result - expected) < 0.01
        mock_preprocessor.transform.assert_called_once_with(input_df)
        mock_model.predict.assert_called_once()

    def test_small_prediction(self):
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[0.1, 0.2]])

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([10.0])

        input_df = pd.DataFrame({'feature1': [0.1], 'feature2': [0.2]})
        result = make_prediction(mock_model, input_df, mock_preprocessor)

        # expm1(10.0) = 22025.47...
        assert 22000 < result < 22030

    def test_negative_log_prediction(self):
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[0.0, 0.0]])

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([-1.0])

        input_df = pd.DataFrame({'feature1': [0.0], 'feature2': [0.0]})
        result = make_prediction(mock_model, input_df, mock_preprocessor)

        # expm1(-1.0) = -0.632...
        assert result < 0


# =============================================================================
# Tests for shap_lite_approximation
# =============================================================================
class TestShapLiteApproximation:
    def test_linear_model_coefficients(self):
        """Should compute feature contributions for linear models"""
        lr = LinearRegression()
        lr.coef_ = np.array([0.5, -0.3, 0.8])
        lr.intercept_ = 1000

        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[10.0, -5.0, 8.0]])

        feature_names = np.array(['car_age', 'kms_driven', 'company_BMW'])

        result = shap_lite_approximation(lr, None, mock_preprocessor, feature_names)
        assert len(result) > 0
        assert result[0][0] in feature_names

    def test_tree_model_feature_importances(self):
        """Should compute feature contributions for tree models"""
        rf = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
        rf.fit(np.random.randn(50, 3), np.random.randn(50))

        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[10.0, -5.0, 8.0]])

        feature_names = np.array(['car_age', 'kms_driven', 'company_BMW'])

        result = shap_lite_approximation(rf, None, mock_preprocessor, feature_names)
        assert len(result) > 0
        assert len(result) <= 8

    def test_empty_result_for_no_supported_model(self):
        class DummyModel:
            pass

        mock_model = DummyModel()
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[1.0, 2.0]])

        result = shap_lite_approximation(mock_model, None, mock_preprocessor,
                                          np.array(['a', 'b']))
        assert result == []

    def test_limits_to_8_contributions(self):
        lr = LinearRegression()
        lr.coef_ = np.random.randn(20) * 100
        lr.intercept_ = 0

        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.random.randn(1, 20)

        feature_names = np.array([f'feature_{i}' for i in range(20)])

        result = shap_lite_approximation(lr, None, mock_preprocessor, feature_names)
        assert len(result) <= 8


# =============================================================================
# Tests for ensemble_prediction
# =============================================================================
class TestEnsemblePrediction:
    def test_ensemble_with_top3(self):
        """Should average top-3 model predictions"""
        models = {
            'Linear Regression': MagicMock(),
            'XGBoost': MagicMock(),
            'Gradient Boosting': MagicMock()
        }
        for m in models.values():
            m.predict.return_value = np.array([12.0])

        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[0.5, 0.3]])

        input_df = pd.DataFrame({'feature1': [0.5]})
        mean_pred, spread, color = ensemble_prediction(models, input_df, mock_preprocessor)

        assert mean_pred is not None
        assert abs(spread) < 0.01
        assert color == 'green'

    def test_ensemble_high_variance(self):
        """Should flag high variance predictions with red"""
        models = {
            'Linear Regression': MagicMock(),
            'XGBoost': MagicMock(),
            'Gradient Boosting': MagicMock()
        }
        preds_log = [10.0, 13.0, 16.0]
        for m, p in zip(models.values(), preds_log):
            m.predict.return_value = np.array([p])

        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[0.5, 0.3]])

        input_df = pd.DataFrame({'feature1': [0.5]})
        mean_pred, spread, color = ensemble_prediction(models, input_df, mock_preprocessor)

        assert mean_pred is not None
        assert spread > 20
        assert color == 'red'

    def test_ensemble_medium_variance(self):
        models = {
            'Linear Regression': MagicMock(),
            'XGBoost': MagicMock(),
            'Gradient Boosting': MagicMock()
        }
        # Log-space values close together → ~14% spread in real prices (yellow: 10-20%)
        preds_log = [12.0, 12.07, 12.14]
        for m, p in zip(models.values(), preds_log):
            m.predict.return_value = np.array([p])

        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[0.5, 0.3]])

        input_df = pd.DataFrame({'feature1': [0.5]})
        mean_pred, spread, color = ensemble_prediction(models, input_df, mock_preprocessor)

        assert mean_pred is not None
        assert 10 < spread < 20, f"Expected spread 10-20%, got {spread:.1f}%"
        assert color == 'yellow'

    def test_ensemble_no_models(self):
        """Should return None when no models available"""
        mean_pred, spread, color = ensemble_prediction({}, None, None)
        assert mean_pred is None
        assert spread is None
        assert color == 'red'


# =============================================================================
# Tests for MODEL_METRICS data integrity
# =============================================================================
class TestModelMetrics:
    def test_eight_models(self):
        assert len(MODEL_METRICS) == 8

    def test_unique_model_names(self):
        names = [m['Model'] for m in MODEL_METRICS]
        assert len(names) == len(set(names))

    def test_r2_in_range(self):
        for m in MODEL_METRICS:
            assert 0 <= m['Test R²'] <= 1, f"{m['Model']} has R²={m['Test R²']}"

    def test_positive_errors(self):
        for m in MODEL_METRICS:
            assert m['RMSE'] > 0, f"{m['Model']} has RMSE={m['RMSE']}"
            assert m['MAE'] > 0, f"{m['Model']} has MAE={m['MAE']}"

    def test_time_non_negative(self):
        for m in MODEL_METRICS:
            assert m['Time (s)'] >= 0, f"{m['Model']} has Time={m['Time (s)']}"

    def test_linear_regression_best(self):
        best = max(MODEL_METRICS, key=lambda x: x['Test R²'])
        assert best['Model'] == 'Linear Regression'

    def test_metrcs_df_columns(self):
        expected_cols = ['Model', 'Test R²', 'RMSE', 'MAE', 'Time (s)', 'Params']
        for col in expected_cols:
            assert col in METRICS_DF.columns, f"Missing column: {col}"


# =============================================================================
# Tests for CURRENT_YEAR
# =============================================================================
class TestConstants:
    def test_current_year(self):
        assert CURRENT_YEAR == 2025
