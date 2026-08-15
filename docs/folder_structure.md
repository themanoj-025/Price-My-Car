# Folder Structure — Price-My-Car (AutoIntel)

Annotated tree of the **current (post-restructure)** layout, one-line purpose per entry.

```
Price-My-Car/
├── .github/
│   ├── CODEOWNERS / PULL_REQUEST_TEMPLATE.md / ISSUE_TEMPLATE/
│   ├── copilot-instructions.md   # Agent/Copilot conventions (paths kept current)
│   ├── dependabot.yml / labeler.yml
│   └── workflows/                # ci.yml, codeql, gitleaks, labeler, maintenance, stale, welcome
├── .gitignore / .dockerignore / .editorconfig / .gitattributes
├── .streamlit/
│   └── config.toml               # Streamlit runtime config (dark theme, headless)
├── .vscode/settings.json
├── AGENTS.md                     # Agent operating instructions
├── app/                          # Application package (Streamlit)
│   ├── __init__.py
│   ├── streamlit_app.py          # Entry point: streamlit run app/streamlit_app.py
│   └── helpers.py                # Pure, testable business/helper functions
├── data/
│   └── Cleaned_Car_data.csv      # Committed dataset (11,149 cleaned records)
├── docs/
│   ├── architecture.md · folder_structure.md · module_dependency.md
│   ├── startup_flow.md · package_overview.md
│   ├── migration/                # migration_summary, old_tree_to_new_tree, file_move_ledger
│   ├── community/ design/ product/ project/ reference/ technical/
├── Dockerfile                    # Multi-target: base → deps → prod / dev
├── docker-compose.yml            # Base compose (prod target)
├── docker-compose.dev.yml        # Dev override: bind mounts + hot reload
├── docker-compose.prod.yml       # Prod compose
├── LICENSE / Makefile / README.md / PROJECT_ANALYSIS.md / PROJECT_OVERVIEW.md
├── ml_ready/                     # ML artifacts (kept — pkl/npy path contract)
│   ├── preprocessor.pkl · feature_names.pkl
│   ├── models/*.pkl              # 8 trained models
│   └── models/*_gs_results.json  # GridSearchCV results
├── notebooks/
│   └── car_price_ml_comparison.ipynb  # Algorithm comparison notebook (generated)
├── pyproject.toml / requirements.txt
├── scripts/
│   ├── admin/                    # Dev/ops tooling
│   │   ├── create_notebook.py    #   → notebooks/car_price_ml_comparison.ipynb
│   │   ├── debug_dtypes.py       #   dtype inspector for the CSV
│   │   └── generate_report.py    #   → report_output/ HTML EDA report
│   ├── backfills/                # Data preparation (regenerates derived artifacts)
│   │   └── prepare_ml_data.py    #   CSV → ml_ready/*.npy + preprocessor.pkl
│   └── seed/                     # Model artifact seeding
│       ├── train_dashboard_models.py   # → ml_ready/models/*.pkl
│       └── tune_hyperparameters.py     # → ml_ready/models/*_gs_results.json
├── setup.sh                      # Streamlit Cloud bootstrap (prep + train if missing)
└── tests/
    ├── __init__.py
    └── test_helpers.py           # 65 unit tests for app/helpers.py
```

## Top-level folder purposes

| Path | Purpose |
| --- | --- |
| `app/` | Application code — entry point + shared helpers, as a package. |
| `scripts/` | Operational Python tooling, split by role: `admin/` (tools), `backfills/` (data prep), `seed/` (model artifacts). |
| `tests/` | Test suite (package layout for clean imports). |
| `data/` | Committed datasets. |
| `notebooks/` | Jupyter notebooks. |
| `ml_ready/` | ML artifacts (models, preprocessor) — **path contract** with app + scripts + Docker. |
| `docs/` | Documentation suite, categorized. |
| `.github/` | CI/CD + community health files. |
| Root files | Canonical metadata + runtime infra (`Dockerfile`, compose, `Makefile`, `setup.sh`). |
