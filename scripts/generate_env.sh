#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" # import usefull functions
DSDC_DIR="${DSDC_DIR:-$(find_project_root .dsdc_project_root)}"

# Écrire dans un .env complet pour docker-compose
env_file=$DSDC_DIR/services/.env

cat $DSDC_DIR/.env.secrets > $env_file

POSTGRES_DB=$(yq e '.services.postgres.db_name' $DSDC_DIR/config.yaml)
echo "POSTGRES_DB=$POSTGRES_DB" >> $env_file