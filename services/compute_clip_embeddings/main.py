from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from PIL import Image
import io
import logging

from dsdc.models.clip import CLIPSingleton

app = FastAPI(
    title="Compute CLIP Embeddings Service",
    description="Micro-service pour calculer les embeddings CLIP d'une image et d'un texte.",
    version="1.0.0"
)

model = CLIPSingleton()

import tempfile
from pathlib import Path

@app.post("/compute-embeddings")
async def compute_embeddings(image: UploadFile = File(...), text: str = Form(...)):
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image JPEG ou PNG.")

    try:
        # Sauvegarde temporaire de l'image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            contents = await image.read()
            tmp_file.write(contents)
            tmp_path = Path(tmp_file.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement de l'image : {e}")

    try:
        embeddings = model.get_embeddings([tmp_path], [text])
    except Exception as e:
        logging.exception("Erreur lors du calcul des embeddings.")
        raise HTTPException(status_code=500, detail=f"Erreur dans le modèle CLIP : {e}")
    finally:
        try:
            tmp_path.unlink()  # Supprime le fichier temporaire
        except Exception as cleanup_error:
            logging.warning(f"Impossible de supprimer le fichier temporaire : {cleanup_error}")

    return JSONResponse(content={
        "embeddings": embeddings[0],
        "version": model.version
    })