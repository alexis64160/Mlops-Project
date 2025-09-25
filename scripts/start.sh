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

# generate docker-compose .env file
env_file=$DSDC_DIR/services/.env
cat $DSDC_DIR/.env.secrets > $env_file

POSTGRES_DB=$(yq e '.services.postgres.db_name' $DSDC_DIR/config.yaml)
echo "POSTGRES_DB=$POSTGRES_DB" >> $env_file

cd $DSDC_DIR/services
export AIRFLOW_UID=$(id -u)
docker-compose up -d

