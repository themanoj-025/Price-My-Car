# Architecture — Price-My-Car (AutoIntel)

> Production-ready Streamlit ML application for used-car price prediction in the
> Indian market: 8 ML models, 9 dashboard pages, auth + admin panel, single
> deployable Streamlit app.

---

## 1. System Overview

```
                        ┌───────────────────────────────────────────────┐
   data/                │                   app/                        │
   Cleaned_Car_data.csv │  streamlit_app.py ──imports──► helpers.py     │
        │               │       │                        │              │
        │               │       │ (CWD-relative loads)   │              │
        │               └───────┼────────────────────────┼──────────────┘
        │                       │                        │
        ▼                       ▼                        ▼
   scripts/backfills/      ml_ready/*.npy          ml_ready/preprocessor.pkl
   prepare_ml_data.py ──►  (X_train, X_test,       + ml_ready/models/*.pkl
        │                  y_train, y_test,             │
        │                  feature_names)               │
        │                                               │
        ▼                        ┌──────────────────────┘
   scripts/seed/
   ├─ tune_hyperparameters.py ──► ml_ready/models/*_gs_results.json
   └─ train_dashboard_models.py ─► ml_ready/models/*.pkl

   scripts/admin/
   ├─ generate_report.py ──► report_output/ (HTML EDA report)
   ├─ create_notebook.py ──► notebooks/car_price_ml_comparison.ipynb
   └─ debug_dtypes.py (dev debug tool)

   Orchestration: Dockerfile (prod/dev) · docker-compose*.yml · setup.sh (Streamlit Cloud)
   Quality gates:  .github/workflows/ci.yml (py_compile + pytest) · Makefile · tests/
```

## 2. Major Components

| Component | Location | Responsibility |
| --- | --- | --- |
| Dashboard entry | `app/streamlit_app.py` | Streamlit entry point (launched via `streamlit run app/streamlit_app.py`). Auth (bcrypt + JSON persistence), 9 pages, admin panel, demo-mode fallback. |
| Shared logic | `app/helpers.py` | Pure, Streamlit-free helper functions (formatting, prediction, ensemble, deal score, SHAP-lite, report generation). Unit-tested. |
| Data prep | `scripts/backfills/prepare_ml_data.py` | Loads `data/Cleaned_Car_data.csv`, log1p-transforms the target, engineers 39 features, splits, and writes `ml_ready/*.npy` + `preprocessor.pkl`. Run at Docker build time and by `setup.sh`. |
| Tuning | `scripts/seed/tune_hyperparameters.py` | GridSearchCV over GB/XGB/RF; writes tuned models + `*_gs_results.json` into `ml_ready/models/`. |
| Training | `scripts/seed/train_dashboard_models.py` | Trains the 8 dashboard models with tuned params; writes `ml_ready/models/*.pkl`. |
| Reporting | `scripts/admin/generate_report.py` | Generates `report_output/car_price_eda_report.html` (EDA visualizations). |
| Notebook builder | `scripts/admin/create_notebook.py` | Generates `notebooks/car_price_ml_comparison.ipynb` (algorithm comparison). |
| Debug tool | `scripts/admin/debug_dtypes.py` | Prints dtypes of the cleaned CSV (dev/ops aid). |
| Dataset | `data/Cleaned_Car_data.csv` | Committed raw data (11,149 cleaned records). Read CWD-relatively by app + scripts. |
| ML artifacts | `ml_ready/` | Committed `.pkl` models + preprocessor; gitignored generated `.npy`/`.csv` intermediates. |
| Tests | `tests/test_helpers.py` | 65 unit tests over `app/helpers.py` (no Streamlit/browser needed). |
| Runtime infra | `Dockerfile` (prod/dev targets), `docker-compose*.yml`, `setup.sh`, `Makefile` | Build, run, hot-reload, Streamlit-Cloud bootstrap, dev ergonomics. |
| CI | `.github/workflows/ci.yml` | Syntax check + pytest + compose validation + Docker build + trivy scan. |

## 3. Runtime Model

- **Process**: a single Streamlit server. No REST API, no workers, no queue.
- **State**: `users_db.json` (created at runtime, bind-mounted in dev) holds bcrypt-hashed
  users + prediction history. `st.session_state` holds per-session UI/auth state.
- **Caching**: `@st.cache_data`/`@st.cache_resource` memoize data, preprocessor, models,
  and preprocessed arrays across sessions.
- **Degradation**: if artifacts are missing, the app falls back to **demo mode**
  (synthetic data) with a clear banner — never a crash.

## 4. Path & Import Strategy (why the moves are safe)

- All data/artifact reads are **CWD-relative** (`data/Cleaned_Car_data.csv`,
  `ml_ready/...`), and every entry point is invoked from the repo root
  (`streamlit run app/streamlit_app.py`, `python scripts/...`), so runtime paths are
  unchanged.
- `app/streamlit_app.py` bootstraps the repo root onto `sys.path` before
  `from app.helpers import ...`, making `app` importable as a package regardless of
  CWD or launch method.
- `tests/` is a package (`tests/__init__.py`) so pytest's prepend-import mode places
  the repo root on `sys.path`, resolving `from app.helpers import ...` from tests.

## 5. Cross-cutting Concerns

- **Security**: bcrypt password hashing; admin authorization re-verified server-side
  against `users_db.json`; CI scans for secrets; trivy scans the built image.
- **Deployment**: Docker multi-target builds; Streamlit Cloud via `setup.sh` bootstrap;
  healthcheck on `/_stcore/health`.
- **ML determinism**: log1p target transform is applied consistently in prep, training,
  and inference (`helpers.py`), with `np.expm1` inversion at prediction time.

See also: `docs/module_dependency.md`, `docs/startup_flow.md`, `docs/package_overview.md`,
`docs/migration/old_tree_to_new_tree.md`.
