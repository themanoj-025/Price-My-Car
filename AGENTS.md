# AGENTS.md — Price-My-Car

> Canonical project instructions. Pointers like `CLAUDE.md` or
> `.github/copilot-instructions.md` should say "See AGENTS.md".

---

## Project overview

**Price-My-Car** — a car pricing estimator + comparison dashboard. Core
components:

- **API** — FastAPI service for pricing estimates.
- **Web / App** — frontend consuming the API.
- **Pricing** — pricing model and calculators.
- **Dashboard** — Streamlit app for reviewing estimates.

Stack: Python 3.11+ · FastAPI · Streamlit.

---

## Exact commands

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Lint / typecheck / test
make lint
pre-commit run --all-files
python -m mypy . --ignore-missing-imports
python -m pytest tests/ -v --cov=. --cov-fail-under=70

# Run
uvicorn api.main:app --reload
streamlit run dashboard/app.py
```

---

## Folder map

| Path | Purpose |
|------|---------|
| `api/` | FastAPI application (routes, services) |
| `pricing/` | Pricing model + calculators |
| `dashboard/` | Streamlit dashboard |
| `tests/` | pytest suite |
| `.github/workflows/` | CI (ruff, mypy, pytest, gitleaks, trivy) |

## Do / don't

- **Do** keep the pricing model behind a stable service class so inputs
  and outputs are explicit.
- **Do not** commit `.env` files.
- **Do not** commit vehicle VIN data that could identify a real car.

## Security rules

- No secrets in the repository; `gitleaks` CI gate gates on hits.
- VIN and owner data must be masked or tokenized before any file leaves
  the sandbox.

## AI-assistance convention

Commits authored by AI must carry the trailer:

```text
AI-Assisted: yes | no | partial
```

See `.gitmessage` for the template. Do not rewrite historic commits
retroactively.
