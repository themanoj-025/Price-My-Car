# Contributing to Price-My-Car

Thank you for your interest in contributing to Price-My-Car, the used car price prediction application!

## Getting Started

### Prerequisites
- Python 3.x
- pip

### Setup
1. Fork and clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Prepare the data and train models:
   ```bash
   python prepare_ml_data.py
   python train_dashboard_models.py
   ```

### Running the Application
```bash
streamlit run streamlit_app.py
```

### Hyperparameter Tuning (Optional)
```bash
python tune_hyperparameters.py
```

### Generating Reports (Optional)
```bash
python generate_report.py
```

## Code Style

- Follow PEP 8 conventions.
- Use 4-space indentation.
- Add docstrings to functions, especially data processing and ML training code.
- Use descriptive variable names that reflect the car domain (e.g., `km_driven`, `fuel_type`).

## Project Structure

- **`streamlit_app.py`** — Main web application with sidebar inputs and prediction display
- **`helpers.py`** — Data loading, preprocessing, prediction aggregation, formatting
- **`prepare_ml_data.py`** — Data cleaning and feature engineering pipeline
- **`train_dashboard_models.py`** — Multi-model training with evaluation
- **`tune_hyperparameters.py`** — Grid search and randomized search for optimal params
- **`Cleaned_Car_data.csv`** — Cleaned Indian car market dataset
- **`ml_ready/`** — Saved preprocessor and feature names (pickle)

### ML Pipeline
- Feature preprocessing uses scikit-learn `Pipeline` and `ColumnTransformer`.
- Categorical features: one-hot encoding
- Numerical features: standard scaling
- Models: Linear Regression, Lasso, Ridge, Random Forest, Gradient Boosting, XGBoost
- Evaluation metrics: R², MAE, RMSE

## Running Tests

```bash
python test_helpers.py
```

There is no formal pytest suite. The test file `test_helpers.py` validates helper functions.

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make focused, minimal changes.
3. Re-run the data preparation and training pipeline to verify nothing breaks.
4. Test the Streamlit app manually with a few car configurations.
5. Commit with a descriptive message:
   - Format: `type(scope): description`
   - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
   - Example: `feat(model): add LightGBM to the ensemble`
   - Example: `fix(ui): correct fuel type dropdown options`
6. Push and open a Pull Request.

## Reporting Issues

Include in your report:
- Steps to reproduce
- Whether the issue is in the UI, training, or data processing
- Error messages and stack traces
- Whether models are trained (check `ml_ready/preprocessor.pkl` exists)

## Adding Features

### Adding a new ML model
1. Add the model to `train_dashboard_models.py` following the existing pattern.
2. Add it to the prediction ensemble in `helpers.py`.
3. Update evaluation metrics display in `streamlit_app.py` if needed.

### Adding new car features
1. Update `prepare_ml_data.py` to include the new feature in preprocessing.
2. Update the Streamlit form in `streamlit_app.py` with the new input.
3. Retrain models.

### Dataset Notes
- The dataset is specific to the Indian car market.
- Fields include: make, model, year, fuel type, transmission, owner type, km driven, mileage, engine CC, max power, seats, location.
- The target variable is the selling price.
- See `car_price_ml_comparison.ipynb` for exploratory data analysis.

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.
