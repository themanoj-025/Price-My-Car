# Old Tree → New Tree — Price-My-Car

Restructure performed **2026-08-11** per the Principal Architect Enterprise Repository
Restructuring protocol. All moves used `git mv` (history/blame preserved). **No
business logic changed** — only file locations, import statements, and reference
paths (Dockerfile, compose, Makefile, CI, setup.sh, docs).

## Before (2026-08-10)

```
Price-My-Car/
├── .github/ … (unchanged)
├── .streamlit/config.toml
├── AGENTS.md · Dockerfile · docker-compose*.yml · LICENSE · Makefile
├── README.md · PROJECT_ANALYSIS.md · PROJECT_OVERVIEW.md
├── pyproject.toml · requirements.txt · setup.sh
├── car_price_ml_comparison.ipynb        ← root
├── Cleaned_Car_data.csv                 ← root
├── create_notebook.py · debug_dtypes.py ← root
├── docs/
│   ├── architecture.md                  (stub)
│   ├── folder_structure.md              (stub)
│   ├── migration_summary.md             ← root of docs/
│   └── community/ design/ product/ project/ reference/ technical/
├── generate_report.py · helpers.py      ← root
├── ml_ready/ (models/ + preprocessor.pkl)
├── prepare_ml_data.py                   ← root
├── streamlit_app.py · test_helpers.py   ← root
├── train_dashboard_models.py · tune_hyperparameters.py ← root
```

## After (2026-08-11)

```
Price-My-Car/
├── .github/ … (unchanged)
├── .streamlit/config.toml
├── AGENTS.md · Dockerfile · docker-compose*.yml · LICENSE · Makefile
├── README.md · PROJECT_ANALYSIS.md · PROJECT_OVERVIEW.md
├── pyproject.toml · requirements.txt · setup.sh
├── app/
│   ├── __init__.py                     (NEW)
│   ├── helpers.py                      (moved)
│   └── streamlit_app.py                (moved)
├── data/
│   └── Cleaned_Car_data.csv            (moved)
├── docs/
│   ├── architecture.md                 (REWRITTEN)
│   ├── folder_structure.md             (REWRITTEN)
│   ├── module_dependency.md            (NEW)
│   ├── startup_flow.md                 (NEW)
│   ├── package_overview.md             (NEW)
│   ├── migration/
│   │   ├── migration_summary.md        (moved)
│   │   ├── old_tree_to_new_tree.md     (NEW)
│   │   └── file_move_ledger.md         (NEW)
│   └── community/ design/ product/ project/ reference/ technical/
├── ml_ready/ (unchanged — contract)
├── notebooks/
│   └── car_price_ml_comparison.ipynb   (moved)
├── scripts/
│   ├── admin/
│   │   ├── create_notebook.py          (moved)
│   │   ├── debug_dtypes.py             (moved)
│   │   └── generate_report.py          (moved)
│   ├── backfills/
│   │   └── prepare_ml_data.py          (moved)
│   └── seed/
│       ├── train_dashboard_models.py   (moved)
│       └── tune_hyperparameters.py     (moved)
└── tests/
    ├── __init__.py                     (NEW)
    └── test_helpers.py                 (moved)
```

## Summary

| Kind | Count |
| --- | --- |
| Files moved (`git mv`) | 12 |
| New files | 5 (`app/__init__.py`, `tests/__init__.py`, `module_dependency.md`, `startup_flow.md`, `package_overview.md`) + 2 migration docs |
| Docs rewritten | 2 (`architecture.md`, `folder_structure.md`) |
| Deleted | 0 |
| Business logic changes | 0 |
| Import/path fixes | `app/streamlit_app.py` (sys.path bootstrap + `app.helpers` import + 2 CSV paths), `tests/test_helpers.py` (package import), 3 scripts (CSV path), `create_notebook.py` (notebook output path) |
| Reference updates | Dockerfile (prod+dev), `docker-compose.dev.yml`, `Makefile`, `ci.yml`, `setup.sh`, `labeler.yml`, `copilot-instructions.md`, `README.md`, `PROJECT_OVERVIEW.md` |
