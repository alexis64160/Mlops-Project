#!/usr/bin/env bash
# Usage: source ./scripts/configure.sh

# 🛑 Stop if not sourced
(return 0 2>/dev/null) || {
  echo "This script must be sourced: use 'source ./scripts/configure.sh'" >&2
  exit 1
}

# ─────────────────────────────────────────────────────────────
# Resolve script directory (assumes utils.sh is in the same dir)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/utils.sh"

# ─────────────────────────────────────────────────────────────
# Find project root
export DSDC_DIR="$(find_project_root ".dsdc_project_root")"

# Set default venv location
export DSDC_VENV="${DSDC_VENV:-env}"
if [[ "$DSDC_VENV" = /* ]]; then
  VENV_PATH="$DSDC_VENV"
else
  VENV_PATH="${DSDC_DIR}/${DSDC_VENV}"
fi

# ─────────────────────────────────────────────────────────────
# Activate the venv
if [[ -f "$VENV_PATH/bin/activate" ]]; then
  echo "Activating virtual environment at: $VENV_PATH"
  # shellcheck disable=SC1090
  source "$VENV_PATH/bin/activate"
else
  echo "⚠️  Virtual environment not found at: $VENV_PATH"
  echo "Run ./scripts/initialize.sh to create it."
  return 1
fi

cd $DSDC_DIR
# ─────────────────────────────────────────────────────────────
# Summary
echo "✅ Environment configured:"
echo "  - DSDC_DIR=$DSDC_DIR"
echo "  - VENV activated: $VENV_PATH"