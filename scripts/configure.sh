#!/usr/bin/env bash
# Usage: source ./scripts/configure.sh

# 🛑 Stop if not sourced
(return 0 2>/dev/null) || {
  echo "🛑 This script must be sourced: use 'source ./scripts/configure.sh'" >&2
  return 1
}

# Set script directory
if [ "${ZSH_VERSION+set}" ]; then
  SCRIPT_DIR="${0:A:h}"
elif [ "${BASH_VERSION+set}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  echo "🛑 Unsupported shell. Use Bash or Zsh." >&2
  return 1
fi

# Load functions and set project root directory
source "$SCRIPT_DIR/subscripts/utils.sh" 
source "$SCRIPT_DIR/subscripts/set_project_dir.sh" 

# Set default venv location
export DSDC_VENV="${DSDC_VENV:-$DSDC_DIR/.venv}"
if [[ "$DSDC_VENV" = /* ]]; then
  VENV_PATH="$DSDC_VENV"
else
  VENV_PATH="${DSDC_DIR}/${DSDC_VENV}"
fi

# ─────────────────────────────────────────────────────────────
# Activate the venv
if [[ -f "$VENV_PATH/bin/activate" ]]; then
  echo "Activating virtual environment at: $VENV_PATH"
  source "$VENV_PATH/bin/activate"
else
  echo "🛑 Virtual environment not found at: $VENV_PATH"
  echo "Run ./scripts/initialize.sh to create it."
  return 1
fi

cd $DSDC_DIR
# ─────────────────────────────────────────────────────────────
# Summary
echo "✅ Environment configured:"
echo "  - DSDC_DIR set to $DSDC_DIR"
echo "  - VENV activated: $VENV_PATH"