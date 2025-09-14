#!/usr/bin/env bash
set -euo pipefail

# Resolve and source utils.sh (assumes utils.sh is next to this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Find project root
DSDC_DIR="${DSDC_DIR:-$(find_project_root .dsdc_project_root)}"

# generate docker-compose .env file
env_file=$DSDC_DIR/services/.env
cat $DSDC_DIR/.env.secrets > $env_file

POSTGRES_DB=$(yq e '.services.postgres.db_name' $DSDC_DIR/config.yaml)
echo "POSTGRES_DB=$POSTGRES_DB" >> $env_file

cd $DSDC_DIR/services
docker-compose up -d postgres

