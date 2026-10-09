# Testing — AutoIntel: Test Strategy

| Field | Value |
| --- | --- |
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | QA Engineer |
| Status | In Review |

---

## 1. Test Pyramid

```mermaid
graph TD
    E2E[E2E: manual page smoke]
    INT[Integration: model + app]
    UNIT[Unit: helpers - 65 tests]
```

## 2. Strategy

| Layer | Tool | Scope |
| --- | --- | --- |
| Unit | pytest | helpers.py: feature engineering, price bounds, auth, CSV |
| Integration | pytest | Model load + prediction |
| E2E | Manual | 9-page smoke |

Current: **65 unit tests passing** (test_helpers.py).

## 3. Critical Test Cases

| ID | Feature | Case | Expected |
| --- | --- | --- | --- |
| TC-001 | Preprocessing | log1p transform | Skew reduced |
| TC-002 | Predict | Valid features | Price > 0 with CI |
| TC-003 | Predict | Invalid fuel type | Validation error |
| TC-004 | Auth | Wrong password | auth_failed |
| TC-005 | Auth | Admin role gate | admin-only pages |
| TC-006 | CSV | Bad rows | Skipped + reported |
| TC-007 | Depreciation | 5-year curve | Monotonic series |

## 4. Test Data Strategy

- Cleaned_Car_data.csv sample + synthetic fixtures.

## 5. CI Gates

- `pytest test_helpers.py` green.
- Ruff lint.

## 6. Related Documents

| Document | Relationship |
| --- | --- |
| [Rules.md](../project/Rules.md) | Test requirements |
| [PRD.md](../product/PRD.md) | Release criteria |
| [TechSpec.md](TechSpec.md) | Components |
| [AppFlow.md](../design/AppFlow.md) | Flow tests |
| [Schema.md](Schema.md) | Data tests |
| [API.md](API.md) | Contract tests |
| [Design.md](../design/Design.md) | UI tests |
| [ImplementationPlan.md](../project/ImplementationPlan.md) | Test tasks |
| [Tracker.md](../project/Tracker.md) | Status |
| [SecurityAndCompliance.md](SecurityAndCompliance.md) | Security tests |
| [Deployment.md](Deployment.md) | CI gates |
| [Glossary.md](../reference/Glossary.md) | Vocabulary |
| [RiskRegister.md](../project/RiskRegister.md) | Risks |
