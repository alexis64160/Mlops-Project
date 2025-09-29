FROM python:3.13-slim

WORKDIR /app

COPY dsdc ./dsdc
COPY .dsdc_project_root .
COPY .env.secrets .

COPY config.yaml .
# COPY services/predict/main.py .
COPY services/predict/pyproject.toml .

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .
# RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]