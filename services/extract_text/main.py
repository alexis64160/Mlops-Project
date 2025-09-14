# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import io
import logging

app = FastAPI(title="Extract Text Service")


TESSERACT_VERSION = str(pytesseract.get_tesseract_version())

# Si besoin, ajuste le chemin de tesseract ici
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

@app.post("/extract-text")
async def extract_text(image: UploadFile = File(...)):
    if image.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image JPEG, PNG ou TIFF.")

    try:
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logging.error(f"Erreur lors du traitement de l'image : {e}")
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement de l'image : {e}")

    try:
        text = pytesseract.image_to_string(pil_image, lang='eng')
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction du texte : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction du texte : {e}")

    return JSONResponse(content={"extracted_text": text.strip(), "version":TESSERACT_VERSION})