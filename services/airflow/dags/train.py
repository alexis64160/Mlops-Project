from airflow.decorators import dag, task
from datetime import datetime
import logging
import requests
import mlflow
from pathlib import Path

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

@task(task_id="train_model")
def task_train_model():
    API_URL="http://dsdc-train:8000/train-model"
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

@task(task_id="set_up_best_model")
def task_deploy_best_model():
    experiment = mlflow.get_experiment_by_name("daily_model_train")
    if experiment is None:
        logging.warning("Experiment not found.")
        return
    experiment_id = experiment.experiment_id
    runs = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["start_time DESC"],
    )
    best_val = -1.0
    best_model_path = None
    for _, run in runs.iterrows():
        val_acc_list = run.get("metrics.val_accuracy")
        if isinstance(val_acc_list, list):
            val_acc = val_acc_list[-1]
        else:
            val_acc = val_acc_list 
        if val_acc > best_val:
            best_val = val_acc
            best_model_path = run.get("tags.model_name") or run.get("params.model_file")

    if not best_model_path:
        logging.warning("No best model path found.")
        return
    model_file_path = Path(best_model_path)
    current_link = CONFIG.paths.models / "mlps" / "current.keras"
    if current_link.exists() or current_link.is_symlink():
        current_link.unlink()
    current_link.symlink_to(model_file_path)
    logging.info(f"Linked {current_link} -> {model_file_path}")

    # 1. Get OAuth2 token 
    auth_url = "http://dsdc-auth:8000/token"
    auth_data = {
        "username": "airflow",
        "password": "airflow_reload_secret"
    }
    try:
        auth_response = requests.post(
            auth_url, 
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        auth_response.raise_for_status()
        access_token = auth_response.json().get("access_token")
        if not access_token:
            logging.warning("No access token received from auth service.")
            return
    except Exception as e:
        logging.warning(f"Failed to get access token: {e}")
        return

    # 2. use token to launch model reload
    reload_url = "http://dsdc-predict:8000/reload-model"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.post(reload_url, headers=headers)
        if response.status_code == 200:
            logging.info("Successfully reloaded dsdc-predict.")
        else:
            logging.warning(f"Failed to reload dsdc-predict: {response.status_code} {response.text}")
    except Exception as e:
        logging.warning(f"Could not contact dsdc-predict to reload model: {e}")

@dag(
    dag_id="train_model",
    default_args=default_args,
    schedule="50 * * * *",
    catchup=False,
    description="Train 5 models upon current data",
    tags=["dsdc", "train", "model"],
    max_active_runs=1,
)
def dag_train_model():
    task_train_model() >> task_deploy_best_model()

dag = dag_train_model()