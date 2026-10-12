<p align="center">
  <img src="https://img.shields.io/badge/AutoIntel-Used%20Car%20Price%20Intelligence-blue?style=for-the-badge" alt="AutoIntel Logo" />
</p>

<h1 align="center">AutoIntel (Price-My-Car)</h1>

<p align="center">
  <strong>Machine learning price valuation and market intelligence platform for the Indian used car market.</strong>
</p>

<p align="center">
  <a href="https://github.com/themanoj-025/Price-My-Car/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/themanoj-025/Price-My-Car/ci.yml?style=flat-square&label=CI" alt="CI Status" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT" /></a>
  <a href="https://github.com/themanoj-025/Price-My-Car/stargazers"><img src="https://img.shields.io/github/stars/themanoj-025/Price-My-Car?style=social" alt="GitHub Stars" /></a>
  <a href="https://github.com/themanoj-025/Price-My-Car/issues"><img src="https://img.shields.io/github/issues/themanoj-025/Price-My-Car?style=flat-square" alt="GitHub Issues" /></a>
  <a href="https://github.com/themanoj-025/Price-My-Car/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome" /></a>
</p>

---

## Overview

AutoIntel estimates used automobile valuations and delivers automotive market intelligence tailored to the Indian pre-owned vehicle marketplace. Evaluating over 11,000 sanitized market listings across 36 manufacturers, the platform features 8 benchmarked regression estimators (including tuned Linear Regression, Ridge, and XGBoost models) with target log-transformation to manage extreme price skewness.

The project offers an interactive 9-page Streamlit portal with user authentication alongside a production-ready FastAPI REST inference service.

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Dataset Characteristics](#dataset-characteristics)
- [Model Performance Benchmark](#model-performance-benchmark)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Quick Start](#installation--quick-start)
- [REST API Reference](#rest-api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Support](#support)

---

## Key Features

- **Multi-Model Valuation Lab**: Benchmarks 8 distinct regression models (Linear Regression, Ridge, XGBoost, Gradient Boosting, SVR, Lasso, KNN, Random Forest).
- **Interactive Multi-Page Portal**: 9 dedicated dashboard pages covering exploratory data analysis, market trends, residual diagnostic plots, batch CSV predictions, and admin controls.
- **Depreciation & Confidence Analysis**: Generates projected price degradation curves based on mileage and chronological vehicle age alongside statistical prediction intervals.
- **FastAPI REST Inference**: Exposes high-throughput prediction routes protected with optional Bearer token authentication and slowapi rate limits.
- **Target Skewness Correction**: Applies log1p transformations, reducing target distribution skewness from 5.64 to -0.12 for superior linear convergence.

---

## Architecture

```text
       Indian Used Car Dataset (11K+ Cleaned Listings)
                            │
                            ▼
               Feature Engineering Pipeline
       (Log1p Target Transform, One-Hot & Scaling)
                            │
                            ▼
                  Model Training & Benchmarking
       (GridSearchCV Hyperparameter Optimization)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
  Streamlit Application (9 Pages)     FastAPI REST Service
     (app/streamlit_app.py)           (app/api_server.py)
            │                               │
            └───────────────┬───────────────┘
                            ▼
                  End-User Valuations
```

---

## Dataset Characteristics

The baseline cleaned dataset contains 11,149 verified vehicle listings:

| Field | Description | Range / Categories |
| :--- | :--- | :--- |
| `name` | Make and model denomination | Hundreds of distinct model variants |
| `company` | Automotive manufacturer | 36 distinct brands (Maruti, Hyundai, Honda, etc.) |
| `year` | Manufacturing registration year | 1996 through 2024 |
| `kms_driven` | Recorded odometer mileage | Scaled continuous numeric |
| `fuel_type` | Powertrain classification | Petrol, Diesel, CNG, LPG, Electric |
| `Price` | Valuation / selling price | INR ₹20,000 through ₹1,00,00,000 |

---

## Model Performance Benchmark

Evaluation metrics recorded on held-out test splits:

| Model Architecture | Test R² | Test RMSE (INR) | Test MAE (INR) |
| :--- | :--- | :--- | :--- |
| **Linear Regression (Log-Target)** | **0.7654** | ₹2,47,535 | ₹1,36,979 |
| **Ridge Regression (Tuned)** | 0.7605 | ₹2,50,108 | ₹1,36,875 |
| **XGBoost Regressor (Tuned)** | 0.7463 | ₹2,57,436 | ₹1,31,764 |
| **Gradient Boosting** | 0.7373 | ₹2,61,980 | ₹1,32,826 |
| **Support Vector Regressor (SVR)** | 0.6998 | ₹2,80,045 | ₹1,37,355 |

---

## Project Structure

```text
Price-My-Car/
├── app/
│   ├── api_server.py       # FastAPI REST prediction endpoints
│   ├── helpers.py          # Pure Python utility functions (isolated from Streamlit)
│   ├── streamlit_app.py    # Main 9-page Streamlit portal
│   └── ...                 # Additional application logic
├── data/                   # Raw and transformed vehicle datasets
├── scripts/
│   ├── admin/              # Diagnostic report and notebook generator scripts
│   ├── backfills/          # Feature engineering and dataset preparation
│   └── seed/               # Hyperparameter tuning and model retraining scripts
├── tests/                  # Pytest unit and regression tests
├── Dockerfile              # Multi-stage production container build
├── docker-compose.yml      # Local container orchestration
├── pyproject.toml          # Build backend and test settings
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## Prerequisites

- **Python**: `>= 3.10`
- **Memory**: Minimum 1 GB RAM

---

## Installation & Quick Start

### 1. Clone & Setup Environment

```bash
# Clone repository
git clone https://github.com/themanoj-025/Price-My-Car.git
cd Price-My-Car

# Create virtual environment
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Run the Applications

**Run Streamlit Portal**:
```bash
streamlit run app/streamlit_app.py
```
*Open http://localhost:8501. Default demo credentials: username `demo` / password `demo123`.*

**Run FastAPI Server**:
```bash
uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --reload
```
*Open Swagger documentation at http://localhost:8000/docs.*

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service liveness probe |
| `GET` | `/api/v1/cars/stats` | Summary statistics and price ranges |
| `GET` | `/api/v1/cars/brands` | List of available manufacturer brands |
| `GET` | `/api/v1/cars/fuel-types`| Valid powertrain categories |
| `POST` | `/api/v1/predict` | Predict car valuation from vehicle attributes |

### Example Request (`POST /api/v1/predict`)

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Maruti",
    "name": "Maruti Suzuki Swift",
    "year": 2018,
    "kms_driven": 45000,
    "fuel_type": "Petrol"
  }'
```

---

## Configuration

| Environment Variable | Default | Purpose |
| :--- | :--- | :--- |
| `PRICE_MY_CAR_API_KEY` | `""` | Optional Bearer authentication secret token |
| `PRICE_MY_CAR_CORS_ORIGINS` | `http://localhost:8501,...` | Permitted browser origins |
| `LOG_DIR` | `logs` | Local destination for structured application logs |

---

## Testing

```bash
# Run full pytest suite
pytest tests/ -v
```

---

## Docker Deployment

```bash
# Start containerized services
docker compose up -d --build
```

---

## Roadmap

- [x] 8 benchmarked regression estimators
- [x] Target log-transformation preprocessing pipeline
- [x] 9-page interactive Streamlit dashboard
- [x] FastAPI REST serving with rate limiting
- [ ] Regional RTO state-registration price variance factors <!-- TODO: Track via GitHub issue -->
- [ ] Automated web scraper for real-time market listing updates <!-- TODO: Track via GitHub issue -->

---

## Contributing

Contributions are welcomed! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for pull request guidelines.

---

## Security

Please report vulnerabilities following the guidance in [SECURITY.md](SECURITY.md).

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

- 🐛 **Issue Tracker**: [GitHub Issues](https://github.com/themanoj-025/Price-My-Car/issues)
- 💡 **Feedback & PRs**: [GitHub Pull Requests](https://github.com/themanoj-025/Price-My-Car/pulls)
