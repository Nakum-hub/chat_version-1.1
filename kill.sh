#!/usr/bin/env bash
# ============================================================
# kill.sh  —  Linux / macOS / WSL
#
# Windows users — you have two options:
#
#   Option A: WSL (recommended)
#     Open a WSL terminal and run:
#       ./kill.sh
#
#   Option B: PowerShell — kill by port manually:
#     # Kill backend (port 8000):
#     Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
#     # Kill frontend (port 4321):
#     Get-Process -Id (Get-NetTCPConnection -LocalPort 4321).OwningProcess | Stop-Process -Force
#
#   Option C: Task Manager
#     Open Task Manager → Details tab → find python.exe and
#     node.exe processes and End Task.
# ============================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDS_FILE="$ROOT/.runall.pids"

kill_by_port() {
  local port=$1
  local pid
  pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [ -n "$pid" ]; then
    echo "Killing process on port $port (PID $pid)..."
    kill "$pid" 2>/dev/null || true
  fi
}

if [ -f "$PIDS_FILE" ]; then
  read -r BACKEND_PID FRONTEND_PID < "$PIDS_FILE"
  for pid in $BACKEND_PID $FRONTEND_PID; do
    if kill -0 "$pid" 2>/dev/null; then
      echo "Killing PID $pid..."
      kill "$pid" 2>/dev/null || true
    fi
  done
  rm -f "$PIDS_FILE"
else
  echo "No PID file found — falling back to port scan..."
  kill_by_port 8000
  kill_by_port 4321
fi

echo "Done."
