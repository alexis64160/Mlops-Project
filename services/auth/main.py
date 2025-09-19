from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time, jwt, os

app = FastAPI(title="Auth API")
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ALGO   = "HS256"
JWT_EXP_S  = int(os.getenv("JWT_EXP_S", "3600"))

class Creds(BaseModel):
    username: str
    password: str

@app.post("/token")
def issue_token(creds: Creds):
    if not (creds.username and creds.password):
        raise HTTPException(status_code=401, detail="invalid")
    payload = {"sub": creds.username, "exp": int(time.time()) + JWT_EXP_S}
    return {"access_token": jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO),
            "token_type": "bearer", "expires_in": JWT_EXP_S}
