from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from dsdc.data.process_text import process_text, PROCESSING_VERSION

app = FastAPI(title="Process Text Service")


class TextIn(BaseModel):
    raw_text: str


@app.post("/process-text")
async def process_text_endpoint(payload: TextIn):
    raw_text = payload.raw_text
    try:
        processed = process_text(raw_text)
    except Exception as e:
        logging.error(f"Erreur lors du traitement du texte : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du texte : {e}")

    return JSONResponse(content={"processed_text": processed, "version": PROCESSING_VERSION})