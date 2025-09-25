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

cd $DSDC_DIR/services
docker-compose down

