FROM python:3.13-slim

WORKDIR /app

COPY dsdc ./dsdc
COPY .dsdc_project_root .
COPY config.yaml .
COPY services/auth/main.py .
COPY services/auth/pyproject.toml .


# Installer tesseract OCR + langues anglaises

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
