docker volume create dsdc_db

docker run -d \
  --name dsdc_postgres_init \
  -e POSTGRES_USER=dsdc_admin \
  -e POSTGRES_PASSWORD=my_strong_password \
  -e POSTGRES_DB=postgres \
  -v dsdc_db:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15


echo "⏳ Waiting for PostgreSQL to be ready (timeout: 10s)..."

MAX_RETRIES=10
RETRY_INTERVAL=1
attempt=1

while ! docker exec dsdc_postgres_init pg_isready -U dsdc_admin -d postgres >/dev/null 2>&1; do
  if [[ $attempt -ge $MAX_RETRIES ]]; then
    echo "❌ PostgreSQL is still not ready after ${MAX_RETRIES} seconds. Exiting."
    exit 1
  fi
  echo "⏳ Attempt $attempt/$MAX_RETRIES... still waiting"
  attempt=$((attempt + 1))
  sleep $RETRY_INTERVAL
done

echo "✅ PostgreSQL is ready!"
docker exec -i dsdc_postgres_init psql -U dsdc_admin -d postgres < $DSDC_DIR/services/postgres/init_dbs/init_dbs_and_users.sql
docker exec -i dsdc_postgres_init psql -U dsdc_service -d dsdc_db < $DSDC_DIR/services/postgres/init_dbs/init_dsdc.sql

docker container stop dsdc_postgres_init

echo "✅ Successfully initialized psql databases"
