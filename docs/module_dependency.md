# Module Dependency — Price-My-Car

Runtime and build-time dependency graph. **No circular imports** — the graph is a
strict DAG flowing data → artifacts → app.

## 1. Dependency Graph

```
                     ┌─────────────────────────────────────────────────┐
                     │                 app/ package                    │
                     │                                                 │
                     │  app/streamlit_app.py ──imports──► app/helpers.py│
                     └───────┬───────────────────────────┬─────────────┘
                             │ (CWD-relative reads)      │ (CWD-relative reads)
                             ▼                           ▼
                     data/Cleaned_Car_data.csv    ml_ready/preprocessor.pkl
                                                 ml_ready/models/*.pkl
                                                 ml_ready/*.npy (generated)
                             ▲                           ▲
                             │                           │ writes
                     ┌───────┴──────────────┐   ┌────────┴─────────────┐
                     │ scripts/backfills/   │   │ scripts/seed/        │
                     │ prepare_ml_data.py   │   │ tune_hyperparameters │
                     │  (reads CSV)         │   │ train_dashboard_models│
                     └──────────────────────┘   └──────────────────────┘

   scripts/admin/generate_report.py ──reads──► data/Cleaned_Car_data.csv ──► report_output/
   scripts/admin/create_notebook.py ───────────────────────────────────► notebooks/*.ipynb
   scripts/admin/debug_dtypes.py   ──reads──► data/Cleaned_Car_data.csv

   tests/test_helpers.py ──imports──► app/helpers.py (only)

   Infra:
     Dockerfile prod  : app/ + scripts/backfills/ + data/ + ml_ready/ + .streamlit/ → RUN prep → CMD streamlit run app/streamlit_app.py
     Dockerfile dev   : above + tests/
     compose dev      : bind-mounts app/, tests/, scripts/, data/, ml_ready/, users_db.json
     setup.sh         : scripts/backfills/prepare_ml_data.py + scripts/seed/train_dashboard_models.py
     Makefile/CI      : py_compile app/*.py + pytest tests/
```

## 2. Module Dependency Matrix

| Module | Reads | Writes | Depends on | Consumed by |
| --- | --- | --- | --- | --- |
| `app/streamlit_app.py` | `data/Cleaned_Car_data.csv`, `ml_ready/*` | `users_db.json` (runtime) | `app.helpers` (package import, sys.path bootstrap) | `streamlit run` (local/Docker/Cloud) |
| `app/helpers.py` | — (pure functions) | — | numpy, pandas, joblib, sklearn | `app/streamlit_app.py`, `tests/test_helpers.py` |
| `scripts/backfills/prepare_ml_data.py` | `data/Cleaned_Car_data.csv` | `ml_ready/*.npy`, `ml_ready/preprocessor.pkl`, `ml_ready/*.csv` | pandas, numpy, sklearn, joblib | Dockerfile build, `setup.sh` |
| `scripts/seed/tune_hyperparameters.py` | `ml_ready/*.npy` | `ml_ready/models/*_gs_results.json` (+ tuned pkl) | sklearn, xgboost | manual / ops |
| `scripts/seed/train_dashboard_models.py` | `ml_ready/*.npy` | `ml_ready/models/*.pkl` | joblib, sklearn, xgboost | `setup.sh`, manual |
| `scripts/admin/generate_report.py` | `data/Cleaned_Car_data.csv` | `report_output/` | matplotlib, seaborn, pandas | manual / ops |
| `scripts/admin/create_notebook.py` | — | `notebooks/car_price_ml_comparison.ipynb` | nbformat | manual / dev |
| `scripts/admin/debug_dtypes.py` | `data/Cleaned_Car_data.csv` | stdout | pandas | dev |
| `tests/test_helpers.py` | `app/helpers.py` | — | pytest, sklearn | CI (`pytest tests/test_helpers.py`), Makefile |
| `ml_ready/` | — | — | (written by prep/tune/train) | app + train scripts |

## 3. Why This Shape

- **Leaf-first layering**: `scripts/*` are independent leaves (no internal imports),
  invoked by explicit path from root — CWD-relative artifact paths stay valid.
- **Single seam for artifacts**: `ml_ready/` is the only cross-cutting contract between
  prep/training and the app; it is never renamed without a coordinated update (see
  ledger/backlog).
- **`app` is a package**: `app/__init__.py` + `tests/__init__.py` let both Streamlit and
  pytest import `app.helpers` uniformly; the sys.path bootstrap in `streamlit_app.py`
  covers non-package launch (bare `streamlit run`).

## 4. Change Warnings

- **Renaming `ml_ready/`** touches `app/streamlit_app.py` (~8 refs), 3 scripts, the
  notebook cells, Dockerfile, compose, `setup.sh`, `labeler.yml`, `.gitignore`,
  README, PROJECT_OVERVIEW — do it in one commit with a grep sweep afterwards.
- **Moving `data/Cleaned_Car_data.csv`** requires updating 4 Python readers, the
  Dockerfile `COPY data/`, and the compose bind mount.
- **`app/streamlit_app.py` path bootstrap** must stay the first import-related
  statement — removing it breaks bare `streamlit run`.
