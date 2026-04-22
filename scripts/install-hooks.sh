#!/usr/bin/env bash
# Install git hooks for local CI.
# Run once from the repo root: bash scripts/install-hooks.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$ROOT/.git/hooks"

if [[ ! -d "$HOOKS_DIR" ]]; then
  echo "Error: .git/hooks not found. Run this from inside the repo." >&2
  exit 1
fi

cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/usr/bin/env bash
# Pre-push hook — runs local CI before every push.
# To skip in an emergency: git push --no-verify
ROOT="$(git rev-parse --show-toplevel)"
exec bash "$ROOT/scripts/ci-local.sh"
EOF

chmod +x "$HOOKS_DIR/pre-push"
echo "Installed pre-push hook → .git/hooks/pre-push"
echo "Local CI will run automatically before each push."
echo "To bypass in an emergency: git push --no-verify"
