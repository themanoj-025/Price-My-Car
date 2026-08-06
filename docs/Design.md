# Design — AutoIntel: Design System & UX Principles

| Field | Value |
|---|---|
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | Design Lead |
| Status | In Review |

---

## 1. Design Principles

1. **Decision-first** — every page answers a pricing question.
2. **Confidence visible** — CI and error bars are first-class.
3. **Calm density** — tables + charts lead.
4. **Consistent** — shared components across 13 screens.
5. **Trustworthy** — metrics labeled with model + data provenance.

## 2. Brand & Visual Identity

- Voice: automotive, analytical, trustworthy.
- Imagery: car data visualizations, depreciation curves.

## 3. Color System

| Token | Hex | Usage | Contrast (AA) |
|---|---|---|---|
| bg | `#F8FAFC` | light bg | — |
| surface | `#FFFFFF` | cards | — |
| primary | `#2563EB` | CTAs | 5.9:1 |
| text | `#0F172A` | body | 15:1 |
| muted | `#64748B` | secondary | 4.9:1 |
| success | `#16A34A` | good value | 5.1:1 |
| warning | `#D97706` | fair value | 4.7:1 |
| danger | `#DC2626` | overpriced | 5.9:1 |

## 4. Typography Scale

| Token | Font | Size | Weight | Line-height | Usage |
|---|---|---|---|---|---|
| display | sans | 30px | 700 | 1.2 | price display |
| heading | sans | 20px | 600 | 1.3 | page titles |
| body | sans | 14px | 400 | 1.5 | content |
| price | mono | 24px | 700 | 1.2 | predicted price |
| caption | sans | 12px | 400 | 1.4 | meta |

## 5. Spacing & Grid

- Base 4px; Streamlit layout.
- Breakpoints: Streamlit responsive.

## 6. Component Library

**Price card:**

```
┌────────────────────────────┐
│ Predicted Price            │
│ ₹8,45,000 ± ₹24,000 (95%) │
│ [Depreciation Curve]       │
└────────────────────────────┘
```

**Confidence band chart:** predicted price with CI ribbon.

Other: KPI card, dataset filter panel, model metrics table, residual scatter, calibration curve, batch upload widget, history table.

## 7. Iconography

Plotly + emoji; no image assets.

## 8. Accessibility

- WCAG 2.1 AA targets; value never color-only.

## 9. Responsive

- Fluid Streamlit layout.

## 10. Motion

- Chart transitions (300ms); reduced-motion honored.

## 11. Dark Mode

Light theme default; dark roadmap.

## 12. Related Documents

| Document | Relationship |
|---|---|
| [AppFlow.md](AppFlow.md) | Screens |
| [PRD.md](PRD.md) | UX goals |
| [TechSpec.md](TechSpec.md) | Stack |
| [Schema.md](Schema.md) | Display data |
| [ImplementationPlan.md](ImplementationPlan.md) | Tasks |
| [Tracker.md](Tracker.md) | Status |
| [Rules.md](Rules.md) | Standards |
| [API.md](API.md) | Contracts |
| [SecurityAndCompliance.md](SecurityAndCompliance.md) | Auth |
| [Testing.md](Testing.md) | UI tests |
| [Deployment.md](Deployment.md) | Deploy |
| [Glossary.md](Glossary.md) | Vocabulary |
| [RiskRegister.md](RiskRegister.md) | Risks |
