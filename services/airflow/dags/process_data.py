from airflow.decorators import dag, task
from datetime import datetime

from dsdc.data.ingest import ingest_data
# from dsdc.data.extract_text import extract_texts
# from dsdc.data.process_text import process_texts
# from dsdc.data.process_image import process_images
# from dsdc.data.compute_embeddings import compute_embeddings

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}

@dag(
    dag_id="ingest_and_process_data",
    default_args=default_args,
    schedule="10 * * * *",  # schedule_interval est déprécié, utiliser schedule
    catchup=False,
    description="Ingest and process data",
    tags=["dsdc", "ingest", "process", "data"],
)

def dag_ingest_and_process_data():
    @task(task_id="ingest_data")
    def task_ingest_data():
        ingest_data()
        print("XXX" * 50)
    task_ingest_data()
    # @task(task_id="extract_texts")
    # def task_extract_texts():
    #     extract_texts()

    # @task(task_id="process_texts")
    # def task_process_texts():
    #     process_texts()

    # @task(task_id="process_images")
    # def task_process_images():
    #     process_images()

    # @task(task_id="compute_embeddings")
    # def task_compute_embeddings():
    #     compute_embeddings()
    
    # # Appels des tâches (déclaration des dépendances)
    # t_ingest = task_ingest_data()
    # t_extract = task_extract_texts()
    # t_process_text = task_process_texts()
    # t_process_img = task_process_images()
    # t_embed = task_compute_embeddings()

    # Dépendances
    # t_ingest >> [t_extract, t_process_img]
    # t_extract >> t_process_text
    # [t_process_img, t_process_text] >> t_embed

dag = dag_ingest_and_process_data()