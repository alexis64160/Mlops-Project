FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# RUN pip install --upgrade pip && pip install poetry

WORKDIR /app

COPY services/streamlit/pyproject.toml /app

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .

COPY services/streamlit/main.py /app

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]