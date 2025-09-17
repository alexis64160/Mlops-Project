from airflow.decorators import dag, task
from datetime import datetime
import logging

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}

@dag(
    dag_id="dag_mockup_add_data",
    default_args=default_args,
    schedule="0 * * * *",  # schedule_interval est déprécié, utiliser schedule
    catchup=False,
    description="Génère des données simulées dans data/to_ingest",
    tags=["dsdc", "mock", "add", "data"],
)
def dag_mockup_add_data():
    from dsdc import CONFIG
    from dsdc.data.mock import build_rvl_csv, pull_cdip_images
    @task(task_id="ensure_rvl_csv_exists")
    def ensure_rvl_csv_exists():
        if not CONFIG.paths.rvl_csv.exists():
            build_rvl_csv()

    @task(task_id="add_data_task")
    def add_data_task():
        pull_cdip_images()
    
    ensure_rvl_csv_exists() >> add_data_task()

dag = dag_mockup_add_data()