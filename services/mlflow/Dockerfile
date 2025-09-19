FROM python:3.10-slim
WORKDIR /app
RUN pip install mlflow psycopg2-binary
COPY services/mlflow/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
VOLUME ["/mlruns"]
EXPOSE 5000
CMD ["/app/entrypoint.sh"]
