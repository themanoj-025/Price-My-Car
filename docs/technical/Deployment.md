# Deployment — AutoIntel: Environments, CI/CD, Rollback

|Field|Value|
|---|---|
|Version|v0.1|
|Last Updated|2026-08-06|
|Owner|DevOps Engineer|
|Status|In Review|

---

## 1. Service Topology

|Service|Purpose|Port|
|---|---|---|
|streamlit|App|8501|

## 2. CI/CD Pipeline

```mermaid
graph LR
    A[push] --> B[Lint]
    B --> C[Tests]
    C --> D[Build]
    D --> E[Deploy]
```

## 3. Environment Promotion

|Step|From|To|Trigger|
|---|---|---|---|
|1|main|staging|CI green|
|2|staging|prod (Streamlit Cloud)|manual|

## 4. Rollback Procedure

- Revert commit; re-run training if models change.
- JSON store backups for users.

## 5. Feature Flags

- N/A — env-driven model paths.

## 6. On-Call / Runbook

- **Predictions slow:** check model load.
- **Login broken:** JSON store corruption → restore backup.
- **Missing pages:** verify session auth.

## 7. Related Documents

|Document|Relationship|
|---|---|
|[TechSpec.md](TechSpec.md)|Environments|
|[SecurityAndCompliance.md](SecurityAndCompliance.md)|Deploy policy|
|[PRD.md](../product/PRD.md)|Release criteria|
|[AppFlow.md](../design/AppFlow.md)|Flows|
|[Schema.md](Schema.md)|Data|
|[Design.md](../design/Design.md)|Design|
|[ImplementationPlan.md](../project/ImplementationPlan.md)|Rollout|
|[Tracker.md](../project/Tracker.md)|Status|
|[Rules.md](../project/Rules.md)|Standards|
|[API.md](API.md)|Interfaces|
|[Testing.md](Testing.md)|CI gates|
|[Glossary.md](../reference/Glossary.md)|Vocabulary|
|[RiskRegister.md](../project/RiskRegister.md)|Risks|
