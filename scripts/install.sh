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

source "$SCRIPT_DIR/configure.sh"

# DOWNLOAD CLIP WEIGHTS #
python $DSDC_DIR/dsdc/scripts/download_clip.py

# DOCKER
# ceate volumes
docker volume create dsdc_postgres
docker volume create dsdc_pgadmin
docker volume create dsdc_grafana

# BUILD LOCAL FILES
python $DSDC_DIR/dsdc/scripts/generate_dot_env.py
python dsdc/scripts/generate_init_dbs_sql.py

# BUILD ALL IMAGES
# specific build for airflow image in order to use it for all related containers
cd $DSDC_DIR/services/airflow
docker build -t dsdc-airflow:latest . 
# all other builds
cd $DSDC_DIR/services
docker-compose build

# INITIALIZE POSTGRES #
$DSDC_DIR/scripts/subscripts/initialize_postgres.sh

# INITIALIZE PGADMIN #
$DSDC_DIR/scripts/subscripts/initialize_pgadmin.sh
