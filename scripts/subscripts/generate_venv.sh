#!/usr/bin/env bash

# 🛑 Stop if not sourced
(return 0 2>/dev/null) || {
  echo "🛑 This script must be sourced" >&2
  return 1
}

if [[ ! -n "$DSDC_DIR" ]]; then
  echo "🛑 Unable to generate venv while DSDC_DIR is not set" >&2
  return 1
fi

if [[ ! -n "$DSDC_DIR" ]]; then
  echo "🛑 Unable to generate venv while DSDC_PYTHON is not set" >&2
  return 1
fi

# Step 0: Define path variables
TMP_VENV=$DSDC_DIR/tmp/venv
DSDC_VENV="${DSDC_VENV:-.venv}"
if [[ "$DSDC_VENV" = /* ]]; then # absolute path
  VENV_DIR="$DSDC_VENV"
else # relative path
  VENV_DIR="${DSDC_DIR}/${DSDC_VENV}"
fi

# Step 1: Create temporary venv
echo "[INFO] Creating temporary bootstrap venv: $TMP_VENV"
$DSDC_PYTHON -m venv "$TMP_VENV"
source "$TMP_VENV/bin/activate"

# Step 2: Install uv in temporary venv
pip install --quiet uv

# Step 3: Use uv to create final project venv
echo "[INFO] Creating project venv at $VENV_DIR using uv"
uv venv "$VENV_DIR"

# Step 3.5: Ensure pip is available in the final venv BEFORE activation
"$VENV_DIR/bin/python" -m ensurepip --upgrade
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

# Step 4: Cleanup temporary venv
deactivate
rm -rf "$TMP_VENV"
echo "[INFO] Cleaned up temporary bootstrap venv."

# Step 5: Activate the final venv and install uv + dsdc
source "$VENV_DIR/bin/activate"
pip install --quiet uv
uv pip install -e .
