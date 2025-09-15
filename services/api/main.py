from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from PIL import Image
import io
import httpx

from .ml.predictor import predict  # <-- on va l’écrire juste après

app = FastAPI(title="Document Recognition API", version="0.1.0")

# CORS (autorise les appels depuis un front en dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en prod: remplace par la liste de tes domaines
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlPayload(BaseModel):
    url: HttpUrl

@app.get("/health")
def health():
    return {"status": "ok"}

async def _fetch_image_from_url(url: str) -> Image.Image:
    """
    Télécharge l'image depuis le web et renvoie une PIL.Image en RGB.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            raise HTTPException(400, f"Téléchargement impossible (HTTP {resp.status_code}).")
        content_type = resp.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise HTTPException(415, f"Le contenu récupéré n'est pas une image (Content-Type: {content_type}).")
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except httpx.RequestError as e:
        raise HTTPException(400, f"Erreur réseau: {e}") from e
    except Exception as e:
        raise HTTPException(400, f"Image invalide: {e}") from e

@app.post("/classify-url")
async def classify_url(payload: UrlPayload):
    """
    JSON: {"url": "https://....jpg"}
    """
    image = await _fetch_image_from_url(str(payload.url))
    result = predict(image)
    return result

@app.post("/classify-file")
async def classify_file(file: UploadFile = File(...)):
    """
    form-data: file=@mon_image.jpg
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(415, f"Le fichier n'est pas une image (Content-Type: {file.content_type}).")
    data = await file.read()
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Image invalide: {e}")
    result = predict(image)
    return result
