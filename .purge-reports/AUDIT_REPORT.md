# DEAD-WEIGHT PURGE v2.0 AUDIT REPORT

**Repository**: `Price-My-Car`  
**Mode**: `AUDIT_ONLY` (Zero repository modifications performed)  
**Baseline Commit SHA**: `821266f562dba9252e63df994d720c6e29c8b74d`  
**Audit Date**: 2026-10-11  
**Verdict**: **YELLOW** (Dead weight detected; review recommended)

---

## 1. Executive Summary

- **Tracked Files in Git**: 141
- **Untracked Local Files**: 0
- **Total LOC**: 31,853
- **Analyzed Size**: 1.48 MB
- **Total Dead-Weight Candidates Identified**: 103
  - **Tier 0 (Provable Junk/Empty)**: 79
  - **Tier 1 (High Confidence)**: 0
  - **Tier 2 (Medium / Needs Verification)**: 24
  - **Tier 3 (Protected / Hard Vetoed)**: 0

## 2. Findings by Category

| Category | Description | Count |
|---|---|---|
| **A** | Empty & Near-Empty Files | 2 |
| **C** | Junk / Caches / Build Artifacts | 77 |
| **D** | Potential Orphan Modules | 24 |
| **H** | Exact Hash Duplicates | 0 |

### Top Tier-0 Items (Provable Deletion Candidates if EXECUTE_SAFE were used):
- [`A`] `app/py.typed`: 0-byte file with no content
- [`A`] `py.typed`: 0-byte file with no content
- [`C`] `.cleanup-audit/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.cleanup-audit/.claude/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.coverage`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.github/copilot-instructions.md`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.hypothesis/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.hypothesis/.gitignore`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.hypothesis/unicode_data/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.mypy_cache/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.mypy_cache/.gitignore`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.mypy_cache/3.11/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.mypy_cache/3.12/`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.mypy_cache/CACHEDIR.TAG`: Untracked build/dependency/cache artifact directory in workspace
- [`C`] `.pytest_cache/`: Untracked build/dependency/cache artifact directory in workspace
_...and 64 more listed in `manifest.csv`._

## 3. Next Steps & Recommended Actions

1. Review `.purge-reports/manifest.csv` and `.purge-reports/FLAGGED.md`.
2. If safe cleanup is desired, configure `MODE: EXECUTE_SAFE` or generate an approval `PLAN.yaml`.
3. Verify that all untracked artifacts (`__pycache__`, `.venv`, `.pytest_cache`) are properly covered in `.gitignore`.
