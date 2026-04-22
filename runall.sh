#!/usr/bin/env bash
# ============================================================
# runall.sh  —  Linux / macOS / WSL
#
# Windows users — you have two options:
#
#   Option A: WSL (recommended)
#     Open a WSL terminal and run this script as-is:
#       ./runall.sh
#
#   Option B: Git Bash (comes with Git for Windows)
#     Run this script from a Git Bash terminal:
#       bash runall.sh
#     Note: 'lsof' is not available in Git Bash — use kill.sh
#     via WSL or run kill.bat instead (see kill.sh comments).
#
#   Manual Windows equivalent (PowerShell):
#     cd backend
#     python -m venv .venv
#     .venv\Scripts\pip install -e ".[dev]"
#     .venv\Scripts\python -m alembic -c alembic/alembic.ini upgrade head
#     .venv\Scripts\python -m app.db.seed
#     Start-Process .venv\Scripts\python -ArgumentList "-m uvicorn app.main:app --reload --port 8000"
#     cd ..\frontend-astro
#     npm install
#     Start-Process npm -ArgumentList "run dev"
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend-astro"
PIDS_FILE="$ROOT/.runall.pids"

# --- Backend setup ---
echo "[backend] Setting up virtual environment..."
cd "$BACKEND_DIR"

if [ ! -f ".venv/bin/pip" ]; then
  echo "[backend] Creating fresh virtual environment..."
  rm -rf .venv
  python3 -m venv --clear .venv
fi

VENV_PY="$BACKEND_DIR/.venv/bin/python"
VENV_PIP="$BACKEND_DIR/.venv/bin/pip"

echo "[backend] Installing packages..."
"$VENV_PIP" install -q -e ".[dev]"

if [ ! -f ".env" ]; then
  echo "[backend] No .env found — copying .env.example"
  cp .env.example .env
fi

echo "[backend] Running migrations..."
"$VENV_PY" -m alembic -c alembic/alembic.ini upgrade head

echo "[backend] Seeding database..."
"$VENV_PY" -m app.db.seed || true   # non-fatal if already seeded

echo "[backend] Starting uvicorn on :8000..."
"$VENV_PY" -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# --- Frontend setup ---
cd "$FRONTEND_DIR"

if [ ! -f ".env" ]; then
  echo "[frontend] No .env found — copying .env.example"
  cp .env.example .env
fi

echo "[frontend] Installing npm packages..."
npm install --silent

echo "[frontend] Starting Astro dev server on :4321..."
npm run dev &
FRONTEND_PID=$!

# --- Save PIDs ---
echo "$BACKEND_PID $FRONTEND_PID" > "$PIDS_FILE"

echo ""
echo "Running:"
echo "  Backend  → http://localhost:8000  (PID $BACKEND_PID)"
echo "  Frontend → http://localhost:4321  (PID $FRONTEND_PID)"
echo ""
echo "Run ./kill.sh to stop both."

wait
