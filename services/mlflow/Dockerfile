FROM ghcr.io/mlflow/mlflow

RUN pip install psycopg2-binary

RUN apt-get update && apt-get install git -y

CMD mlflow server \
    --backend-store-uri postgresql://mlflow:mlflow_strong_password@postgres:5432/mlflow \
    --default-artifact-root /mlflow/artifacts \
    --host 0.0.0.0 \
    --port 5000