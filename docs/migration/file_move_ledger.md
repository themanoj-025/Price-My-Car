# File Move Ledger — Price-My-Car

Restructure date: **2026-08-11** · Method: `git mv` (rename tracking, history preserved)
· Branch: `main` (local commits, no push).

## Moved Files

| # | Old Path | New Path | Category | Reason | Risk | Verified? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `streamlit_app.py` | `app/streamlit_app.py` | App → `app/` | Feature-owned app package with single entry | Medium (sys.path bootstrap added) | ✅ pytest + py_compile |
| 2 | `helpers.py` | `app/helpers.py` | App → `app/` | Co-locate shared logic with entry point | Medium (import updated) | ✅ pytest + py_compile |
| 3 | `test_helpers.py` | `tests/test_helpers.py` | Test → `tests/` | Canonical test home; package layout for imports | Medium (import updated) | ✅ pytest 65/65 |
| 4 | `prepare_ml_data.py` | `scripts/backfills/prepare_ml_data.py` | Script → `scripts/backfills/` | Data-prep role; invoked from root (CWD paths safe) | Medium (Dockerfile RUN + setup.sh updated) | ✅ docker config + py_compile |
| 5 | `train_dashboard_models.py` | `scripts/seed/train_dashboard_models.py` | Script → `scripts/seed/` | Model-artifact seeding | Medium (setup.sh updated) | ✅ py_compile |
| 6 | `tune_hyperparameters.py` | `scripts/seed/tune_hyperparameters.py` | Script → `scripts/seed/` | Model-artifact seeding | Low | ✅ py_compile |
| 7 | `create_notebook.py` | `scripts/admin/create_notebook.py` | Script → `scripts/admin/` | Dev tooling | Low (output path updated) | ✅ py_compile |
| 8 | `debug_dtypes.py` | `scripts/admin/debug_dtypes.py` | Script → `scripts/admin/` | Dev tooling | Low (CSV path updated) | ✅ py_compile |
| 9 | `generate_report.py` | `scripts/admin/generate_report.py` | Script → `scripts/admin/` | Ops/reporting tool | Low (CSV path updated) | ✅ py_compile |
| 10 | `car_price_ml_comparison.ipynb` | `notebooks/car_price_ml_comparison.ipynb` | Notebook → `notebooks/` | Canonical notebook home | Low (labeler glob updated) | ✅ |
| 11 | `Cleaned_Car_data.csv` | `data/Cleaned_Car_data.csv` | Data → `data/` | Canonical data home | Medium (4 Python readers + Dockerfile + compose updated) | ✅ prep script runs |
| 12 | `docs/migration_summary.md` | `docs/migration/migration_summary.md` | Meta → Docs | Consolidate migration records | Low (no refs) | ✅ |

## New Files

| Path | Reason |
| --- | --- |
| `app/__init__.py` | Package marker for `app` (uniform `from app.helpers import ...`). |
| `tests/__init__.py` | Package marker so pytest prepends repo root to `sys.path`. |
| `docs/module_dependency.md`, `docs/startup_flow.md`, `docs/package_overview.md` | Phase 6 deliverables. |
| `docs/migration/old_tree_to_new_tree.md`, `docs/migration/file_move_ledger.md` | Phase 6 deliverables. |

## Files Rewritten (same path)

| Path | Reason |
| --- | --- |
| `docs/architecture.md` | Stub → full architecture document. |
| `docs/folder_structure.md` | Stub → full annotated tree. |
| `app/streamlit_app.py` | Import fixes only: `import sys`, sys.path bootstrap, `from app.helpers import ...`, CSV path → `data/...`. |
| `tests/test_helpers.py` | Import fix: `from app.helpers import ...`. |
| `scripts/backfills/prepare_ml_data.py`, `scripts/admin/debug_dtypes.py`, `scripts/admin/generate_report.py` | CSV path → `data/Cleaned_Car_data.csv`. |
| `scripts/admin/create_notebook.py` | Notebook output → `notebooks/car_price_ml_comparison.ipynb`. |
| `Dockerfile`, `docker-compose.dev.yml`, `Makefile`, `.github/workflows/ci.yml`, `setup.sh`, `.github/labeler.yml`, `.github/copilot-instructions.md`, `README.md`, `PROJECT_OVERVIEW.md` | Reference paths updated to new locations. |

## Files Deliberately NOT Moved (contract analysis)

| Path | Why it stays | Risk if moved |
| --- | --- | --- |
| `ml_ready/` | Referenced CWD-relatively by app + 3 scripts + notebook cells + Dockerfile + compose + setup.sh + `.gitignore` + labeler | High — >25 references; low value |
| `.streamlit/config.toml` | Streamlit discovers config in the launch CWD | High — breaks theme/headless config |
| `users_db.json` | Runtime auth DB; Makefile/compose contract | High — runtime file |
| `Dockerfile`, compose files, `Makefile`, `setup.sh`, `.gitignore` | Canonical infra at root (protocol allows) | — |

## Flagged (needs human review / backlog)

| Item | Flag |
| --- | --- |
| `ml_ready/` naming | Not a banned token, but `models/` is the target convention; rename deferred (25+ refs) — do as a dedicated follow-up commit with full grep sweep. |
| Root `__pycache__/` | Untracked runtime artifact; gitignored — no action. |
| `users_db.json` in `.gitignore` | Currently **not** ignored (grep: no match); add to `.gitignore` so local auth DBs never get committed. |

## Deletions

None in this restructure (protocol: flag, don't delete).
