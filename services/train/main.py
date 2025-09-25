from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Dict
import logging
from datetime import datetime
import uuid
from dsdc.models.mlp import MLP
from dsdc.db.crud.embeddings import get_embedding_label_pairs
import numpy as np


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
    params: Dict #TODO: specifier

@app.post("/train-model")
async def train_model(request: TrainParams):
    try:
        training_date = datetime.now().isoformat()
        model = MLP(request.params)

        X_train, y_train = load_data()

        history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)

        model_path = f"mlp_{uuid.uuid4()}.keras"
        model.save(model_path)

        training_history = history.history

        # 6. Réponse
        return JSONResponse(content={
            "message": "Modèle entraîné avec succès.",
            "model_file": model_path,
            "history": training_history,
            "training_date": training_date
        })

    except Exception as e:
        logging.exception("Unable to perform training")
        raise HTTPException(status_code=500, detail=str(e))