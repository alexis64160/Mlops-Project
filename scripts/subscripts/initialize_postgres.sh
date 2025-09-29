source $DSDC_DIR/.secrets

docker run -d --rm \
  --name dsdc-postgres-init \
  -e POSTGRES_USER=${POSTGRES_USER} \
  -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
  -e POSTGRES_DB=${POSTGRES_DB} \
  -v dsdc_postgres:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15


echo "⏳ Waiting for PostgreSQL to be ready (timeout: 10s)..."

MAX_RETRIES=10
RETRY_INTERVAL=1
attempt=1

while ! docker exec dsdc-postgres-init pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} >/dev/null 2>&1; do
  if [[ $attempt -ge $MAX_RETRIES ]]; then
    echo "❌ PostgreSQL is still not ready after ${MAX_RETRIES} seconds. Exiting."
    exit 1
  fi
  echo "⏳ Attempt $attempt/$MAX_RETRIES... still waiting"
  attempt=$((attempt + 1))
  sleep $RETRY_INTERVAL
done

echo "✅ PostgreSQL is ready!"
docker exec -i dsdc-postgres-init psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < $DSDC_DIR/services/postgres/init_dbs/init_dbs_and_users.sql
docker exec -i dsdc-postgres-init psql -U ${POSTGRES_DSDC_USER} -d ${POSTGRES_DSDC_DB} < $DSDC_DIR/services/postgres/init_dbs/init_dsdc.sql

docker container stop dsdc-postgres-init

echo "✅ Successfully initialized psql databases"
