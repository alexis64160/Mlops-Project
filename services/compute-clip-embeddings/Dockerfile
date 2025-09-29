FROM python:3.13-slim

WORKDIR /app

COPY dsdc ./dsdc
COPY .dsdc_project_root .

COPY config.yaml .
COPY services/compute-clip-embeddings/main.py .
COPY services/compute-clip-embeddings/pyproject.toml .

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .
RUN python dsdc/scripts/download_clip.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]