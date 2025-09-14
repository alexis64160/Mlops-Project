from airflow.decorators import dag, task
from datetime import datetime

from dsdc import CONFIG
from dsdc.data.mock import build_rvl_csv, pull_cdip_images

def add_data():
    if not CONFIG.paths.rvl_csv.exists():
        build_rvl_csv()
    pull_cdip_images()


default_args = {
    # tes arguments, par ex:
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}

@dag(
    dag_id="dag_mockup_add_data",
    default_args=default_args,
    schedule=None,  # schedule_interval est déprécié, utiliser schedule
    catchup=False,
    description="Génère des données simulées dans data/to_ingest",
    tags=["dsdc", "mock", "add", "data"],
)
def dag_mockup_add_data():

    @task(task_id="mock_add_data")
    def add_data_task():
        add_data()  # ta fonction que tu as déjà définie
    add_data_task()

dag = dag_mockup_add_data()