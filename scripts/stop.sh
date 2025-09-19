#!/usr/bin/env bash
set -euo pipefail

# Resolve and source utils.sh (assumes utils.sh is next to this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
# Find project root
DSDC_DIR="${DSDC_DIR:-$(find_project_root .dsdc_project_root)}"


cd $DSDC_DIR/services
docker-compose down

