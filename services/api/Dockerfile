FROM python:3.10-slim
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.api /app/requirements.txt
RUN pip install -r requirements.txt

# Copier le code de l'API et les modèles
COPY services/api /app
COPY dsdc /app/dsdc
COPY models /app/models

ENV MLFLOW_TRACKING_URI=http://mlflow:5000
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
