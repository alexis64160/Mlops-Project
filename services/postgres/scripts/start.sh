#!/usr/bin/env bash

docker run --rm --name dsdc-postgres \
  -e POSTGRES_USER=dsdc_user \
  -e POSTGRES_PASSWORD=D@h3r50C@T@ \
  -e POSTGRES_DB=dsdc_db \
  -v dsdc_pgdata:/var/lib/postgresql/data \
  -v $DSDC_DIR/services/postgres/.init-db:/docker-entrypoint-initdb.d \
  -p 5432:5432 \
  -d postgres