from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dsdc import CONFIG

# Configuration JWT
SECRET_KEY = os.environ["DSDC_JWT_SECRET_KEY"]
ALGORITHM = getattr(CONFIG.settings, "authenticaiton_algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(CONFIG.settings, "access_token_validity_time_min", 60)

app = FastAPI()

# Hashing des mots de passe
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme pour récupérer le token dans les requêtes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake DB d'utilisateurs
USERS = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Liddell",
        "role": "basic",
        "email": "alice@example.com",
        "hashed_password": pwd_context.hash("wonderland"),
        "disabled": False,
    },
    "airflow": {
        "username": "airflow",
        "full_name": "Airflow orchestrator",
        "role": "model-admin",
        "email": "",
        "hashed_password": pwd_context.hash("airflow"),
        "disabled": False,
    }
}

# Fonctions utilitaires
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoint token

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(USERS, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint protégé exemple

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(USERS, username)
    if user is None:
        raise credentials_exception
    return user
