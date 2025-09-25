from airflow.decorators import dag, task
from datetime import datetime
import logging
import requests
import mlflow

from dsdc import CONFIG
from dsdc.models.mlp_params import get_random_params, INITIAL_BEST_KNWON_PARAMS

# mlflow.set_tracking_uri("file:///opt/dsdc/models/mlruns")
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("daily_model_train")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}

TRAIN_RUNS = 10

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
        reference_time = datetime.now().strftime("%Y%m%d-%H:%M")
        for name, param in params.items():
            run_name = f"{reference_time}_{name}"
            logging.info(f"proceeding for mlflow run {run_name}, with params {param}")
            response = requests.post(API_URL, json={'run_name': run_name, 'params': param})
            if response.status_code == 200:
                result = response.json()
                model_file = result.get("model_file")
                history = result.get("history", {})
                latest_val_accuracy = history["val_accuracy"][-1]
                logging.info(f"Successfully generated model {model_file} (val_acc={latest_val_accuracy})")
                responses.append(response.json())
            else:
                logging.warning("Unable to train model.")
        logging.info(f"Successfully ended task.")
    train = task_train_model() 

dag = dag_train_model()