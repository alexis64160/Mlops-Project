CREATE USER airflow WITH PASSWORD 'airflow_strong_password';
CREATE DATABASE airflow OWNER airflow;
CREATE USER dsdc_service WITH PASSWORD 'dsdc_service_strong_password';
CREATE DATABASE dsdc_db OWNER dsdc_service;
CREATE USER mlflow WITH PASSWORD 'mlflow_strong_password';
CREATE DATABASE mlflow OWNER mlflow;