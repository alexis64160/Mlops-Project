import mlflow
from datetime import datetime
from typing import Dict

# Ici, on configure MLflow pour logguer en local (dossier ./mlruns)
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("document_recognition_api")

def log_prediction(result: Dict):
    """
    Logge une prédiction dans MLflow.
    :param result: dict comme {"label":..., "confidence":..., "width":..., "height":...}
    """
    with mlflow.start_run(run_name=f"prediction-{datetime.now().isoformat()}", nested=True):
        # Log params (input)
        mlflow.log_param("width", result.get("width"))
        mlflow.log_param("height", result.get("height"))

        # Log metrics (outputs)
        mlflow.log_metric("confidence", result.get("confidence", 0.0))

        # Log tag (utile pour filtrer)
        mlflow.set_tag("predicted_label", result.get("label"))

        # (Optionnel) log image : ça peut vite grossir le repo
        # from PIL import Image
        # image.save("tmp.png")
        # mlflow.log_artifact("tmp.png")
