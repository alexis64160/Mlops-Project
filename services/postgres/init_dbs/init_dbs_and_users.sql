CREATE USER dsdc_service WITH PASSWORD 'dsdc_service_strong_password';
CREATE DATABASE dsdc OWNER dsdc_service;

CREATE USER airflow WITH PASSWORD 'airflow_strong_password';
CREATE DATABASE airflow OWNER airflow;

CREATE USER mlflow WITH PASSWORD 'mlflow_strong_password';
CREATE DATABASE mlflow OWNER mlflow;

CREATE USER dsdc_exporter WITH PASSWORD 'dsdc_exporter_strong_password';

-- Read-only permissions for dsdc_exporter on dsdc
GRANT CONNECT ON DATABASE dsdc TO dsdc_exporter;
\c dsdc
GRANT USAGE ON SCHEMA public TO dsdc_exporter;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dsdc_exporter;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dsdc_exporter;

-- Read-only permissions for dsdc_exporter on airflow
GRANT CONNECT ON DATABASE airflow TO dsdc_exporter;
\c airflow
GRANT USAGE ON SCHEMA public TO dsdc_exporter;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dsdc_exporter;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dsdc_exporter;

-- Read-only permissions for dsdc_exporter on mlflow
GRANT CONNECT ON DATABASE mlflow TO dsdc_exporter;
\c mlflow
GRANT USAGE ON SCHEMA public TO dsdc_exporter;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dsdc_exporter;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dsdc_exporter;
