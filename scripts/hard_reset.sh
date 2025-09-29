#!/usr/bin/env bash
set -euo pipefail

# Resolve and source utils.sh (assumes utils.sh is next to this script)
# Set script directory
if [ "${ZSH_VERSION+set}" ]; then
  SCRIPT_DIR="${0:A:h}"
elif [ "${BASH_VERSION+set}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  echo "🛑 Unsupported shell. Use Bash or Zsh." >&2
  return 1
fi

source "$SCRIPT_DIR/configure.sh"

# Load functions and set project root directory
# source "$SCRIPT_DIR/subscripts/utils.sh" 
# source "$SCRIPT_DIR/subscripts/set_project_dir.sh" 

# Ask for confirmation
echo "⚠️  WARNING: This operation will IRREVERSIBLY delete all generated files in:"
echo "  → $DSDC_DIR"
echo
echo "The following will be removed:"
echo "  - Python virtual environment (default: \$DSDC_DIR/env)"
echo "  - All data files"
echo "  - All docker images and containers related to the project"
echo
read -rp "Are you sure you want to proceed? (yes/[no]) " confirm
if [[ "$confirm" != "yes" ]]; then
  echo "Aborted."
  exit 0
fi

echo "🧹 Resetting project at: $DSDC_DIR"

# Resolve venv path
DSDC_VENV="${DSDC_VENV:-.venv}"
if [[ "$DSDC_VENV" = /* ]]; then
  VENV_PATH="$DSDC_VENV"
else
  VENV_PATH="${DSDC_DIR}/${DSDC_VENV}"
fi

# Remove venv
if [[ -d "$VENV_PATH" ]]; then
  echo "🔸 Removing virtual environment: $VENV_PATH"
  rm -rf "$VENV_PATH"
fi

# Remove installed services
echo "🧩 Step: stopping and removing Docker containers..."

# Stop containers whose names start with "dsdc"
CONTAINER_IDS=$(docker ps -a --filter "name=^dsdc" --format "{{.ID}}")
if [[ -n "$CONTAINER_IDS" ]]; then
  echo "$CONTAINER_IDS" | xargs -r docker stop
  sleep 2
  echo "$CONTAINER_IDS" | xargs -r docker rm
else
  echo "ℹ️  No matching containers to stop/remove."
fi

echo "🧩 Step: removing Docker images..."

IMAGE_IDS=$(docker images --filter=reference='dsdc*' -q)
if [[ -n "$IMAGE_IDS" ]]; then
  echo "$IMAGE_IDS" | xargs -r docker rmi
else
  echo "ℹ️  No matching images to remove."
fi

echo "🧩 Step: removing Docker volumes..."

VOLUME_NAMES=$(docker volume ls --format '{{.Name}}' | grep '^dsdc' || true)
if [[ -n "$VOLUME_NAMES" ]]; then
  echo "$VOLUME_NAMES" | xargs -r docker volume rm
else
  echo "ℹ️  No matching volumes to remove."
fi
# Remove tmp dir
if [[ -d "$DSDC_DIR/tmp" ]]; then
  echo "🔸 Removing temporary directory"
  rm -rf "$DSDC_DIR/tmp"
fi

# Remove data dir
if [[ -d "$DSDC_DIR/data" ]]; then
  echo "🔸 Removing data directory"
  rm -rf "$DSDC_DIR/data"
fi

# Remove build dir
if [[ -d "$DSDC_DIR/build" ]]; then
  echo "🔸 Removing build directory"
  rm -rf "$DSDC_DIR/build"
fi

# Remove pytest_cache:
if [[ -d "$DSDC_DIR/.pytest_cache" ]]; then
  echo "🔸 Removing .pytest_cache directory"
  rm -rf "$DSDC_DIR/.pytest_cache"
fi
# Remove dsdc.egg-info:
if [[ -d "$DSDC_DIR/dsdc.egg-info" ]]; then
  echo "🔸 Removing dsdc.egg-info directory"
  rm -rf "$DSDC_DIR/dsdc.egg-info"
fi

# Remove models:
if [[ -d "$DSDC_DIR/models" ]]; then
  echo "🔸 Removing models directory"
  rm -rf "$DSDC_DIR/models"
fi

# Remove logs:
if [[ -d "$DSDC_DIR/logs" ]]; then
  echo "🔸 Removing logs directory"
  rm -rf "$DSDC_DIR/logs"
fi


echo "✅ Hard reset completed."