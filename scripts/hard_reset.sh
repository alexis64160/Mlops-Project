#!/usr/bin/env bash
set -euo pipefail

# Resolve and source utils.sh (assumes utils.sh is next to this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Find project root
DSDC_DIR="$(find_project_root ".dsdc_project_root")"

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
# Stop and remove containers
docker ps -a --filter "name=^dsdc" --format "{{.ID}}" | xargs -r docker stop
docker ps -a --filter "name=^dsdc" --format "{{.ID}}" | xargs -r docker rm
# Remove images
docker images --filter=reference='dsdc*' -q | xargs -r docker rmi
# Remove volumes
docker volume ls --format '{{.Name}}' | grep '^dsdc' | xargs -r docker volume rm

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

echo "✅ Hard reset completed."