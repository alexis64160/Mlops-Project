#!/usr/bin/env bash

source $DSDC_DIR/.env.secret

docker run --rm --name dsdc-postgres \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -e POSTGRES_DB=dsdc_db \
  -v dsdc_pgdata:/var/lib/postgresql/data \
  -v $DSDC_DIR/services/postgres/.init-db:/docker-entrypoint-initdb.d \
  -p 5432:5432 \
  -d postgres