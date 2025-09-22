#!/usr/bin/env bash
set -euo pipefail

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

DSDC_PYTHON=""
cli_python=""

function print_help() {
  cat << EOF >&2
Usage: $(basename "$0") [options]

Options:
  -p, --python PATH        Set the Python executable path (DSDC_PYTHON)
  -h, --help               Display this help message and exit

Examples:
  $(basename "$0") -p /usr/bin/python3.13
  $(basename "$0") --python=/usr/bin/python3.13
EOF
}

function parse_arguments() {

  while [[ $# -gt 0 ]]; do
    case "$1" in
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
}

parse_arguments "$@"

# Resolve DSDC_PYTHON (CLI > ENV (including .env) > DEFAULT)
DSDC_PYTHON=$(check_python_version "$cli_python")


echo "++++++++++++++ $DSDC_DIR"
export DSDC_DIR
export DSDC_PYTHON
cd $DSDC_DIR
# --------------------- #
# CREATE PYTHON UV VENV #
# --------------------- #

source $DSDC_DIR/scripts/subscripts/generate_venv.sh


# --------------------- #
# CREATE TREE STRUCTURE #
# --------------------- #

cd "$DSDC_DIR"
mkdir -p data/raw
mkdir -p data/processed
mkdir -p models

# --------------------- #
# DOWNLOAD CLIP WEIGHTS #
# --------------------- #
python $DSDC_DIR/dsdc/scripts/download_clip.py


# -------------- #
# PREPARE DOCKER #
# -------------- #

docker pull postgres:15
cd $DSDC_DIR/services/airflow
docker build -t dsdc_airflow:latest .
cd $DSDC_DIR
$DSDC_DIR/services/postgres/scripts/initialize.sh


unset DSDC_PYTHON
# TODO: pull toutes images
# TODO: build toutes images
# TODO: prune
