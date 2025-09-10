#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" # import usefull functions

DSDC_DIR=""
DSDC_PYTHON=""

function print_help() {
  cat << EOF >&2
Usage: $(basename "$0") [options]

Options:
  -d, --project-dir DIR    Set the project directory (DSDC_DIR)
  -p, --python PATH        Set the Python executable path (DSDC_PYTHON)
  -h, --help               Display this help message and exit

Examples:
  $(basename "$0") -d /path/to/project -p /usr/bin/python3.13
  $(basename "$0") --project-dir=/path/to/project --python=/usr/bin/python3.13
EOF
}

function parse_arguments() {
  local cli_project_dir=""
  local cli_python=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -d|--project-dir)
        if [[ "$2" && "$2" != -* ]]; then
          cli_project_dir="$2"
          shift 2
        else
          echo "Error: Missing argument for $1" >&2
          print_help
          exit 1
        fi
        ;;
      --project-dir=*)
        cli_project_dir="${1#*=}"
        shift
        ;;
      -p|--python)
        if [[ "$2" && "$2" != -* ]]; then
          cli_python="$2"
          shift 2
        else
          echo "Error: Missing argument for $1" >&2
          print_help
          exit 1
        fi
        ;;
      --python=*)
        cli_python="${1#*=}"
        shift
        ;;
      -h|--help)
        print_help
        exit 0
        ;;
      --)
        shift
        break
        ;;
      -*)
        echo "Unknown option: $1" >&2
        print_help
        exit 1
        ;;
      *)
        break
        ;;
    esac
  done

  # Print the parsed args only on stdout
  printf '%s\n%s\n' "$cli_project_dir" "$cli_python"
}

args=()
while IFS= read -r line; do
  args+=("$line")
done < <(parse_arguments "$@")

cli_project_dir="${args[0]}"
cli_python="${args[1]}"

# Resolve DSDC_DIR (CLI > ENV > DEFAULT)
if [[ -n "$cli_project_dir" ]]; then
  DSDC_DIR="$cli_project_dir"
elif [[ -n "${DSDC_DIR:-}" ]]; then
  DSDC_DIR="$DSDC_DIR"
else
  DSDC_DIR=$(find_project_root ".dsdc_project_root") || true
  if [[ -z "$DSDC_DIR" ]]; then
      echo "Warning: .dsdc_project_root not found, using current directory"
      DSDC_DIR="$(pwd)"
  fi
fi

if [[ ! -f "$DSDC_DIR/.dsdc_project_root" ]]; then
    echo "Warning: Marker file '.dsdc_project_root' not found in project directory '$DSDC_DIR'."
    read -rp "Do you want to continue anyway? [y/N]: " response
    case "$response" in
      [yY][eE][sS]|[yY])
        echo "Continuing despite missing marker file."
        ;;
      *)
        echo "Aborting."
        exit 1
        ;;
    esac
  fi

# Load .env from DSDC_DIR if it exists (only for non-DSDC_DIR variables)
env_file="$DSDC_DIR/.env"
if [[ -f "$env_file" ]]; then
  set -o allexport
  source "$env_file"
  set +o allexport
fi
# Resolve DSDC_PYTHON (CLI > ENV (including .env) > DEFAULT)
DSDC_PYTHON=$(check_python_version "$cli_python")

export DSDC_DIR
export DSDC_PYTHON

# --------------------- #
# CREATE PYTHON UV VENV #
# --------------------- #

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


# --------------------- #
# CREATE TREE STRUCTURE #
# --------------------- #

mkdir -p data/raw
mkdir data/processed

# -------------- #
# PREPARE DOCKER #
# -------------- #
./services/postgres/scripts/initialize.sh



# # création des volumes Docker
# docker volume create dsdc_psql

