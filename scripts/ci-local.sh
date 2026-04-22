#!/usr/bin/env bash
# Local CI — mirrors GitHub Actions checks.
# Run manually or automatically as a pre-push hook (see scripts/install-hooks.sh).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

_header() { echo; echo "==> $*"; }
_ok()     { echo "    OK: $*"; ((PASS++)) || true; }
_err()    { echo "    FAIL: $*"; ((FAIL++)) || true; }

# ── Backend ──────────────────────────────────────────────────────────────────
_header "Backend: pytest"
if (
  cd "$ROOT/backend"
  # Use project venv if available, otherwise fall back to whatever python/pytest is on PATH
  if [[ -x ".venv/bin/pytest" ]]; then
    .venv/bin/pytest --tb=short -q
  elif [[ -x "venv/bin/pytest" ]]; then
    venv/bin/pytest --tb=short -q
  else
    python -m pytest --tb=short -q
  fi
); then
  _ok "All backend tests passed"
else
  _err "Backend tests failed"
fi

# ── Frontend ─────────────────────────────────────────────────────────────────
_header "Frontend: astro check"
if (
  cd "$ROOT/frontend-astro"
  npm run --silent astro -- check
); then
  _ok "TypeScript check passed"
else
  _err "TypeScript check failed"
fi

_header "Frontend: astro build"
if (
  cd "$ROOT/frontend-astro"
  PUBLIC_API_BASE=http://localhost:8000 npx astro build --silent
); then
  _ok "Frontend build succeeded"
else
  _err "Frontend build failed"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo
echo "─────────────────────────────"
echo "  Passed: $PASS  Failed: $FAIL"
echo "─────────────────────────────"

if [[ $FAIL -gt 0 ]]; then
  echo "CI failed. Fix the issues above before pushing."
  exit 1
fi

echo "All checks passed."
