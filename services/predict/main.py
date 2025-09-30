from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from pydantic import BaseModel
import numpy as np
import requests
from dsdc import CONFIG
import os
import logging

VERSION = "v1"
SECRET_KEY = os.environ["DSDC_JWT_SECRET_KEY"]
ALGORITHM = getattr(CONFIG.settings, "authenticaiton_algorithm", "HS256")

# Le tokenUrl doit pointer vers ton service d'auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://dsdc-auth:8000/token")

class TokenData(BaseModel):
    username: str
    role: str

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
    
def require_role(required_role: str):
    def role_checker(user: TokenData = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"User does not have required role: {required_role}"
            )
        return user
    return role_checker


app = FastAPI(title="Process Image Service")

from dsdc.models.mlp import MLP

def load_model(filename="current.keras"):
    model_path = CONFIG.paths.models/"mlps"/filename
    if model_path.exists():
        mlp = MLP.load(filename)
    else: 
        mlp = None
    return mlp
mlp = load_model()

@app.get("/status")
def get_status():
    global mlp
    if mlp is None:
        mlp = load_model()
    if mlp is None:
        raise HTTPException(status_code=503, detail="predict api is unable to load model.")
    else:
        return JSONResponse(content={
            "status": "healthy",
            "version": VERSION
        })

@app.post("/reload-model")
def reload_model(
    current_user: TokenData = Depends(require_role("model-admin"))
):
    global mlp
    if mlp is None:
        mlp = load_model()
    if mlp is None:
        raise HTTPException(status_code=503, detail="predict api is unable to load model.")
    else:
        return JSONResponse(content={
            "message": "Successfully reloaded model",
        })


@app.post(f"/{VERSION}/predict")
async def predict(
    image: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
    ):
    logging.info(f"Prediction requested by user: {current_user}")
    global mlp
    if mlp is None:
        mlp = load_model()
    if mlp is None:
        raise HTTPException(status_code=503, detail="predict api is unable to load model.")
    if image.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image JPEG, PNG ou TIFF.")
    # extract text    
    url = "http://dsdc-extract-text:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc-extract-text:8000/{version}/extract-text"
    payload = {
        "image": (image.filename, await image.read(), image.content_type)
    }
    response = requests.post(url, files=payload)
    raw_text = response.json()["extracted_text"]
    # process text
    url="http://dsdc-process-text:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc-process-text:8000/{version}/process-text"
    response = requests.post(url, json={"raw_text": raw_text})
    processed_text = response.json()["processed_text"]
    # process image
    url = "http://dsdc-process-image:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc-process-image:8000/{version}/process-image"
    await image.seek(0)
    payload = {
        "image": (image.filename, await image.read(), image.content_type)
    }
    response = requests.post(url, files=payload)
    processed_image = response.content
    # compute embeddings
    url = "http://dsdc-compute-clip-embeddings:8000/status"
    response = requests.get(url)
    version = response.json()["version"]
    url = f"http://dsdc-compute-clip-embeddings:8000/{version}/compute-embeddings"
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