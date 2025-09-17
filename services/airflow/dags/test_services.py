import logging
from dsdc.db import SessionLocal
from airflow.decorators import dag, task
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}

@dag(
    dag_id="dag_test_services",
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=["test", "debug"],
)
def test_services():
    @task(task_id="hellow_world")
    def test_hello_world():
        logging.info("Hello world!")

    @task(task_id="test_postgres")
    def test_postgres():
        expected_tables = {
            "original_documents",
            "labels",
            "processed_images",
            "raw_texts",
            "processed_texts",
            "embeddings"
        }
        with SessionLocal() as session:
            response = session.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """).fetchall()
        found_tables = set(r[0] for r in response)
        missing_tables = expected_tables - found_tables
        if missing_tables == set():
            logging.info("All expected tables were retrieved")
        else:
            error_message = f"Following tables were not retrieved: {missing_tables}"
            logging.error(error_message)
            raise ValueError(error_message)
    test_hello_world() >> test_postgres()
dag = test_services()
