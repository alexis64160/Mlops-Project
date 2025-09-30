from dsdc import CONFIG
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
import sys

load_dotenv(CONFIG.paths.project_root/"services"/".env")
sys.path.append(str(CONFIG.paths.project_root))
# from services.auth.main import app as auth_app
# from services.predict.main import app as predict_app
# Clients FastAPI pour chaque service
# auth_client = TestClient(auth_app)
# predict_client = TestClient(predict_app)
USERS = {
    "alice": {
        "username": "alice",
        "password": "wonderland",
        "role": "basic"
    },
    "airflow": {
        "username": "airflow",
        "password": "airflow",
        "role": "model-admin"
    }
}
def test_imports():
    import pandas
    import tensorflow
    import keras

    from fastapi import FastAPI, Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from passlib.context import CryptContext
    from jose import JWTError, jwt
    from datetime import datetime, timedelta
    from typing import Optional
    import os
    from dsdc import CONFIG
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
    assert True
# @pytest.fixture(scope="module")
# def tokens():
#     result = {}
#     for name, user in USERS.items():
#         response = auth_client.post(
#             "/token",
#             data={"username": user["username"], "password": user["password"]},
#             headers={"Content-Type": "application/x-www-form-urlencoded"},
#         )
#         assert response.status_code == 200
#         token = response.json()["access_token"]
#         result[name] = token
#     return result

# def test_predict_access_basic(tokens):
#     headers = {"Authorization": f"Bearer {tokens['alice']}"}
#     files = {'image': ('test.png', b'fake image content', 'image/png')}
#     response = predict_client.post("/v1/predict", headers=headers, files=files)
#     # Accepte succès ou modèle non chargé (503)
#     assert response.status_code in (200, 503)

# def test_predict_access_model_admin(tokens):
#     headers = {"Authorization": f"Bearer {tokens['airflow']}"}
#     files = {'image': ('test.png', b'fake image content', 'image/png')}
#     response = predict_client.post("/v1/predict", headers=headers, files=files)
#     assert response.status_code in (200, 503)

# def test_reload_model_access_denied(tokens):
#     headers = {"Authorization": f"Bearer {tokens['alice']}"}
#     response = predict_client.post("/reload-model", headers=headers)
#     assert response.status_code == 403
#     assert "required role" in response.text

# def test_reload_model_access_granted(tokens):
#     headers = {"Authorization": f"Bearer {tokens['airflow']}"}
#     response = predict_client.post("/reload-model", headers=headers)
#     assert response.status_code in (200, 503)
