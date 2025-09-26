from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import requests

VERSION = "v1"
app = FastAPI(title="Process Image Service")

from dsdc.models.mlp import MLP
filename = "current.keras"
mlp = MLP.load(filename)

@app.get("/status")
def get_status():
    return JSONResponse(content={
        "status": "healthy",
        "version": VERSION
    })

@app.post(f"/{VERSION}/predict")
async def predict(image: UploadFile = File(...)):

    if image.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image JPEG, PNG ou TIFF.")
    # extract text    
    url = "http://dsdc_extract_text:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc_extract_text:8000/{version}/extract-text"
    payload = {
        "image": (image.filename, await image.read(), image.content_type)
    }
    response = requests.post(url, files=payload)
    raw_text = response.json()["extracted_text"]
    # process text
    url="http://dsdc_process_text:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc_process_text:8000/{version}/process-text"
    response = requests.post(url, json={"raw_text": raw_text})
    processed_text = response.json()["processed_text"]
    # process image
    url = "http://dsdc_process_image:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc_process_image:8000/{version}/process-image"
    await image.seek(0)
    payload = {
        "image": (image.filename, await image.read(), image.content_type)
    }
    response = requests.post(url, files=payload)
    processed_image = response.content
    # compute embeddings
    url = "http://dsdc_compute_clip_embeddings:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc_compute_clip_embeddings:8000/{version}/compute-embeddings"
    embeddings_payload = {
        "image": ("processed_image.png", processed_image, "image/png")
    }
    embeddings_data = {
        "text": processed_text
    }
    response = requests.post(url, files=embeddings_payload, data=embeddings_data)
    embeddings = response.json()["embeddings"]
    # prediction
    prediction = mlp.predict(np.array(embeddings).reshape(1, 1024))
    label = int(prediction.argmax())
    probas = prediction.tolist()[0]
    return JSONResponse(
        {"label": label,
         "probas": probas
         }
    )