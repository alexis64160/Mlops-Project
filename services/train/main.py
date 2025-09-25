from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Dict
import logging
from datetime import datetime
import uuid
from dsdc.models.mlp import MLP
from dsdc.models.mlp_params import get_param_summary
from dsdc.db.crud.embeddings import get_embedding_label_pairs
import numpy as np
import mlflow

import logging

logging.basicConfig(
    level=logging.INFO,  # Ou DEBUG
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Train MLP Model",
    description="Train a MLP Model to classify documents from CLIP Embeddings.",
    version="1.0.0"
)

def load_data():
    X, y = get_embedding_label_pairs()
    X = np.array(X) 
    y = np.array(y)
    return X, y

# Structure des paramètres reçus
class TrainParams(BaseModel):
    run_name: str
    params: Dict #TODO: specifier

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("daily_model_train")

@app.post("/train-model")
async def train_model(request: TrainParams):
    run_name = request.run_name
    model_parameters = request.params
    try:
        with mlflow.start_run(run_name=run_name):
            model = MLP(model_parameters)
            X_train, y_train = load_data()
            history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
            model_name = f"mlp_{uuid.uuid4()}.keras"
            model.save(model_name) # custom save function (adds parameters to default Sequential model)
            logging.info(f"Successfully trained and saved model {model_name}.")
            
            # log params
            params_to_log = get_param_summary(params=model_parameters)
            params_to_log["data_size"] = len(X_train)
            mlflow.log_params(params_to_log)
            # log metrics
            training_history = history.history
            for metric_name, values in training_history.items():
                for epoch, metric_value in enumerate(values):
                    mlflow.log_metric(metric_name, metric_value, step=epoch)
            # add tags
            mlflow.set_tag("model_name", model_name)

        return JSONResponse(content={
            "model_file": model_name,
            "history": training_history,
        })

    except Exception as e:
        logging.exception("Unable to perform training")
        raise HTTPException(status_code=500, detail=str(e))