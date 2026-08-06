# Rules — AutoIntel: Coding Standards & AI-Agent Operating Rules

| Field | Value |
| --- | --- |
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | Engineering Lead |
| Status | In Review |

---

## 1. Guiding Principles

1. Testability — helpers must be Streamlit-free (65 unit tests).
2. Readability over cleverness.
3. No silent failures — errors surface in UI.
4. Small PRs only.
5. Evidence-based metrics (R², RMSE, MAE).
6. Auth is required for all pages (except login).

## 2. Code Style

- Python 3.9+, type hints.
- Formatter: black; linter: ruff.
- Structure:

```
streamlit_app.py          # dashboard (auth + 9 pages + admin)
helpers.py                # pure testable helpers
prepare_ml_data.py        # preprocessing
train_dashboard_models.py # training
tune_hyperparameters.py   # GridSearchCV
generate_report.py        # EDA report
create_notebook.py        # notebook builder
test_helpers.py           # 65 tests
```

## 3. Git Workflow

- Branches: `feat/<slug>`, `fix/<slug>`.
- Commits: Conventional Commits.
- PRs: ≤ 400 lines; CI green.
- Merge: squash to main.

## 4. Testing Requirements

- Coverage ≥ 60%; helpers ≥ 80%.
- MUST have tests: feature engineering, price bounds, auth helpers, CSV parsing.
- See [Testing.md](../technical/Testing.md).

## 5. AI Agent Operating Rules

- Always read Tracker.md and ImplementationPlan.md before starting.
- Never mark a task 🟢 Done without tests passing.
- Never invent requirements not in ../product/PRD.md/../technical/TechSpec.md — flag ambiguity.
- Never commit secrets; demo creds documented as demo-only.
- State conflicts rather than silently picking one.

## 6. Security Baseline Rules

- Passwords hashed (never plaintext).
- Demo creds clearly marked demo-only.
- Input validation on prediction form.
- Dependency scans weekly.

## 7. Documentation Rules

- New pages → ../design/AppFlow.md same PR.
- New features → ../product/PRD.md same PR.

## 8. Prohibited Patterns

| Anti-pattern | Why |
| --- | --- |
| Streamlit imports in helpers | Testability |
| Plaintext passwords | Security |
| Hardcoded model paths | Portability |
| Blanket except | Hides failures |

## 9. Escalation Rules

**Ask a human when:** auth model changes, new datasets, scope changes.
**Decide autonomously:** UI polish, tests, model tuning.

## 10. Related Documents

| Document | Relationship |
| --- | --- |
| [Testing.md](../technical/Testing.md) | Test requirements |
| [SecurityAndCompliance.md](../technical/SecurityAndCompliance.md) | Auth |
| [PRD.md](../product/PRD.md) | Requirements |
| [TechSpec.md](../technical/TechSpec.md) | Architecture |
| [AppFlow.md](../design/AppFlow.md) | Flows |
| [Design.md](../design/Design.md) | Design |
| [Schema.md](../technical/Schema.md) | Data |
| [ImplementationPlan.md](ImplementationPlan.md) | Tasks |
| [Tracker.md](Tracker.md) | Status |
| [API.md](../technical/API.md) | Interfaces |
| [Deployment.md](../technical/Deployment.md) | Env vars |
| [Glossary.md](../reference/Glossary.md) | Vocabulary |
| [RiskRegister.md](RiskRegister.md) | Risks |
