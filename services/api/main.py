from fastapi import FastAPI, Header, HTTPException, UploadFile, File
from pydantic import BaseModel
import os, time, jwt, base64, io
from jwt import InvalidTokenError, ExpiredSignatureError
from prometheus_client import Counter, Histogram, make_asgi_app
import mlflow
import logging
from PIL import Image
import torch
import numpy as np
from typing import Optional

# Import du modèle CLIP
import sys
sys.path.append('/app')
from dsdc.models.clip import CLIPSingleton
from dsdc.models.clip_mlp import CLIPBasedMLP

app = FastAPI(title="CLIP Model API")

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ALGO   = os.getenv("JWT_ALGO", "HS256")

def require_auth(authorization: str | None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        # verify signature + exp
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload  # you can use payload["sub"] etc.
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- MLflow tracking ---
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

# --- Prometheus metrics ---
REQS = Counter("clip_total_requests", "Total prediction requests")
LAT  = Histogram("clip_request_latency_seconds", "Prediction latency (s)")

# --- Initialisation du modèle CLIP ---
logging.basicConfig(level=logging.INFO)
try:
    # Initialiser le modèle CLIP
    clip_model = CLIPSingleton()
    logging.info("Modèle CLIP chargé avec succès")
except Exception as e:
    logging.error(f"Erreur lors du chargement du modèle CLIP: {e}")
    clip_model = None

# Classes de documents supportées
DOCUMENT_CLASSES = [
    "letter", "form", "email", "handwritten", "advertisement", 
    "scientific report", "scientific publication", "specification",
    "file folder", "news article", "budget", "invoice", "presentation",
    "questionnaire", "resume", "memo"
]

class DocumentIn(BaseModel):
    content: str  # base64 encoded content
    file_type: str

def extract_text_from_image(image_bytes: bytes) -> str:
    """Extraire le texte d'une image avec OCR"""
    try:
        import pytesseract
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logging.warning(f"Erreur OCR: {e}")
        return ""

def classify_document_with_clip(image_bytes: bytes, text_content: str) -> dict:
    """Classifier un document avec CLIP"""
    if clip_model is None:
        return {"label": "unknown", "score": 0.0, "error": "Modèle CLIP non disponible"}
    
    try:
        # Préparer l'image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Si pas de texte extrait, utiliser OCR
        if not text_content.strip():
            text_content = extract_text_from_image(image_bytes)
        
        # Générer les embeddings avec CLIP
        embeddings = clip_model.get_embeddings(
            image_paths=[image],
            texts=[text_content or "document"]
        )
        
        # Classification simple basée sur la similarité avec les classes
        # Dans un vrai projet, vous utiliseriez un MLP entraîné
        similarities = []
        for doc_class in DOCUMENT_CLASSES:
            # Calculer la similarité avec chaque classe
            class_embeddings = clip_model.get_embeddings(
                image_paths=[image],
                texts=[f"a {doc_class} document"]
            )
            
            # Similarité cosinus
            similarity = np.dot(embeddings[0], class_embeddings[0]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(class_embeddings[0])
            )
            similarities.append((doc_class, similarity))
        
        # Trouver la meilleure correspondance
        best_class, best_score = max(similarities, key=lambda x: x[1])
        
        return {
            "label": best_class,
            "score": float(best_score),
            "all_scores": {cls: float(score) for cls, score in similarities}
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la classification: {e}")
        return {"label": "error", "score": 0.0, "error": str(e)}

@app.post("/predict")
def predict(doc: DocumentIn, authorization: str | None = Header(None)):
    user = require_auth(authorization)
    REQS.inc()
    start = time.time()

    try:
        # Décoder le contenu base64
        file_content = base64.b64decode(doc.content)
        
        # Extraire le texte si c'est une image
        text_content = ""
        if doc.file_type.startswith('image/'):
            text_content = extract_text_from_image(file_content)
        
        # Classification avec CLIP
        prediction = classify_document_with_clip(file_content, text_content)
        prediction["user"] = user.get("sub")

        # Log dans MLflow
        with mlflow.start_run(run_name="inference", nested=True):
            mlflow.log_param("file_type", doc.file_type)
            mlflow.log_param("file_size", len(file_content))
            mlflow.log_param("user", user.get("sub", "unknown"))
            mlflow.log_param("predicted_label", prediction["label"])
            mlflow.log_metric("confidence_score", prediction["score"])
            if "all_scores" in prediction:
                for label, score in prediction["all_scores"].items():
                    mlflow.log_metric(f"score_{label}", score)

        LAT.observe(time.time() - start)
        return {"prediction": prediction}
        
    except Exception as e:
        logging.error(f"Erreur lors de la prédiction: {e}")
        LAT.observe(time.time() - start)
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "clip_loaded": clip_model is not None}

# expose /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
