#!/usr/bin/env bash
set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'
STEP=0; FAILED=0; COMMIT_MSG=""
info() { echo -e "${CYAN}ℹ${NC}  $*"; }
ok() { echo -e "${GREEN}✓${NC}  $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
fail() { echo -e "${RED}✗${NC}  $*"; FAILED=$((FAILED + 1)); }
header() { STEP=$((STEP + 1)); echo ""; echo -e "${BOLD}[Step ${STEP}]${NC} $*"; }
run_check() { local name="$1"; shift; if "$@" 2>&1; then ok "${name}"; else fail "${name}"; return 1; fi; }

DO_COMMIT=true
while [[ $# -gt 0 ]]; do case "$1" in
  --check) DO_COMMIT=false; shift ;;
  -m) COMMIT_MSG="$2"; shift 2 ;;
  -m*) COMMIT_MSG="${1#-m}"; shift ;;
  *) echo "Unknown: $1"; exit 1 ;;
esac; done

header "Git State Check"
git status --porcelain > /dev/null 2>&1 || { fail "Not a git repo"; exit 1; }
if grep -rn '<<<<<<<' --include='*.py' --include='*.html' --include='*.md' . 2>/dev/null | grep -v '.git/' | head -5 >/dev/null 2>&1; then fail "Merge conflict markers detected!"; fi
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ "$BRANCH" = "HEAD" ] && warn "Detached HEAD"
ok "Git state stable (branch: ${BRANCH})"

header "Linting"
if command -v flake8 &>/dev/null; then run_check "flake8" flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.git,__pycache__,venv,.venv || true; fi
if command -v ruff &>/dev/null; then run_check "ruff" ruff check . || true; fi

header "Format"
if command -v black &>/dev/null; then run_check "black check" black --check . --exclude="venv|.venv|__pycache__" 2>/dev/null || warn "Run 'black .' to fix formatting"; fi

header "Type Check"
if command -v mypy &>/dev/null; then run_check "mypy" mypy . --ignore-missing-imports 2>/dev/null || true; fi

header "Tests"
if [ -f "pytest.ini" ] || ls tests/ &>/dev/null 2>&1; then run_check "pytest" python -m pytest . -v --tb=short 2>/dev/null || true; fi

header "Security"
if command -v bandit &>/dev/null; then run_check "bandit" bandit -r . -x venv,__pycache__ -l 2>/dev/null || true; fi
if git diff --cached --name-only | grep -q '\.env$'; then fail ".env file staged!"; fi

header "Staging Safety"
DANGEROUS="__pycache__|\.pyc|\.egg|dist|build|\.venv|venv|\.cache|\.pytest_cache|coverage|logs"
STAGED=$(git diff --cached --name-only | grep -E "$DANGEROUS" || true)
if [ -n "$STAGED" ]; then fail "Dangerous files staged"; echo "$STAGED" | while read -r f; do git reset HEAD "$f" 2>/dev/null || true; done; fi

echo ""; echo "═══════════════════════════════════════════"
if [ "$FAILED" -eq 0 ]; then
  echo -e "${GREEN}${BOLD}  ✓ All checks passed!${NC}"
  echo "═══════════════════════════════════════════"
  if [ "$DO_COMMIT" = true ] && [ -n "$COMMIT_MSG" ]; then git commit -m "$COMMIT_MSG" && echo -e "${GREEN}✓ Commit successful${NC}"; fi
else
  echo -e "${RED}${BOLD}  ✗ ${FAILED} check(s) failed. Commit BLOCKED.${NC}"; exit 1
fi
