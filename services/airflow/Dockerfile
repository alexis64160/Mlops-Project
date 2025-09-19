# Dockerfile
FROM apache/airflow:3.0.6

# Ajoute les dépendances Python
COPY pyproject.toml .

# Installe les packages
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .