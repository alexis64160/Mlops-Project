#!/usr/bin/env bash
set -e
mlflow server   --backend-store-uri postgresql://mlflow:mlflow_pass@postgres:5432/mlflow_db   --default-artifact-root file:/mlruns   --host 0.0.0.0 --port 5000
