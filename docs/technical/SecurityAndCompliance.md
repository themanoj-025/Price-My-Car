# SecurityAndCompliance — AutoIntel: Security

|Field|Value|
|---|---|
|Version|v0.1|
|Last Updated|2026-08-06|
|Owner|Security Engineer|
|Status|In Review|

---

## 1. Threat Model (STRIDE)

|Threat|Surface|Impact|Mitigation|
|---|---|---|---|
|Spoofing|Login|Unauthorized access|Hashed passwords|
|Tampering|Prediction input|Bad outputs|Validation|
|Info disclosure|User data|Privacy|Session-scoped|
|DoS|Heavy compute|Slow app|Limits (small scale)|
|Elevation|Admin|Config tamper|Role checks|

## 2. Auth / Authorization

- Username + hashed password (JSON store).
- Roles: user / admin; admin panel gated.
- Demo creds (demo/demo123) clearly marked demo-only.

## 3. Data Classification

|Data|Class|Handling|
|---|---|---|
|username|PII-ish|masked logs|
|password_hash|credential|hashed|
|car data|public|—|
|prediction history|personal|session/user-scoped|

## 4. Encryption

- In transit: TLS on hosted deploy.
- At rest: passwords hashed.

## 5. Compliance Checklist

- [ ] Passwords hashed
- [ ] Demo creds documented demo-only
- [ ] No secrets in repo
- [ ] Dependency scans

## 6. Incident Response Plan (outline)

1. Detect.
2. Triage.
3. Contain: rotate creds.
4. Remediate.
5. Recover.
6. Postmortem.

## 7. Related Documents

|Document|Relationship|
|---|---|
|[Rules.md](../project/Rules.md)|Security rules|
|[API.md](API.md)|Auth contract|
|[Schema.md](Schema.md)|Sensitive map|
|[TechSpec.md](TechSpec.md)|NFRs|
|[PRD.md](../product/PRD.md)|Goals|
|[AppFlow.md](../design/AppFlow.md)|Flows|
|[Design.md](../design/Design.md)|Design|
|[ImplementationPlan.md](../project/ImplementationPlan.md)|Tasks|
|[Tracker.md](../project/Tracker.md)|Status|
|[Testing.md](Testing.md)|Security tests|
|[Deployment.md](Deployment.md)|Deploy|
|[Glossary.md](../reference/Glossary.md)|Vocabulary|
|[RiskRegister.md](../project/RiskRegister.md)|Risks|
