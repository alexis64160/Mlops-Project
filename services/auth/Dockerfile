FROM python:3.10-slim
WORKDIR /app
COPY services/auth/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY services/auth /app
ENV JWT_SECRET=change-me
EXPOSE 7000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
