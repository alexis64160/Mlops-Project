from airflow.decorators import dag, task
from datetime import datetime
import logging
import requests

from dsdc import CONFIG

from dsdc.models.mlp_params import get_random_params, INITIAL_BEST_KNWON_PARAMS

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}

TRAIN_RUNS = 3

@dag(
    dag_id="train_model",
    default_args=default_args,
    schedule="0 2 * * *",  # schedule_interval est déprécié, utiliser schedule
    catchup=False,
    description="Train 5 models upon current data",
    tags=["dsdc", "train", "model"],
    max_active_runs=1,
)

def dag_train_model():
    @task(task_id="train_model")
    def task_train_model():
        API_URL="http://dsdc_train:8000/train-model"
        params = INITIAL_BEST_KNWON_PARAMS | get_random_params(amount=max(0, TRAIN_RUNS-len(INITIAL_BEST_KNWON_PARAMS)))
        logging.info(f"retrieved {len(params)} parameters sets.")
        responses = []
        for name, param in params.items():
            logging.info(f"generating_model for {name} with params {param}")
            response = requests.post(API_URL, json={'params': param})
            if response.status_code == 200:
                logging.info("Successfully generated model.")
                responses.append(response.json())
            else:
                logging.warning("dsdc_train was not able to train model.")
        logging.info(f"Successfully ended task.")
    
    train = task_train_model() 

dag = dag_train_model()