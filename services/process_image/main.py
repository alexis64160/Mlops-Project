from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
import io
import logging

VERSION = "v1"
app = FastAPI(title="Process Image Service")

@app.get("/status")
def get_status():
    return JSONResponse(content={
        "status": "healthy",
        "version": VERSION
    })

@app.post(f"/{VERSION}/process-image")
async def process_image(image: UploadFile = File(...)):
    if image.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image JPEG, PNG ou TIFF.")

    try:
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logging.error(f"Erreur lors de l'ouverture de l'image : {e}")
        raise HTTPException(status_code=400, detail="Erreur lors du traitement de l'image.")

    try:
        # Redimensionnement façon CLIP
        resized = pil_image.resize((224, 224), resample=Image.BICUBIC)
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        buffer.seek(0)

    except Exception as e:
        logging.error(f"Erreur lors du redimensionnement ou de la sauvegarde : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du traitement de l'image.")

    return StreamingResponse(buffer, media_type="image/png")