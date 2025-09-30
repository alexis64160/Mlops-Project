import pytest
import requests
import os
from dsdc import CONFIG
from dotenv import load_dotenv

load_dotenv(CONFIG.paths.project_root/"services"/".env")

API_URL = f"http://localhost:{os.environ['DSDC_PROCESS_TEXT_PORT']}"
RAW_TEXT = "This is some sample raw text to process."

def get_version():
    response = requests.get(f"{API_URL}/status")
    response.raise_for_status()  # Pour échouer immédiatement si /status ne marche pas
    return response.json().get("version")

def test_status():
    response = requests.get(f"{API_URL}/status")

    assert response.status_code == 200
    json_response = response.json()

    assert json_response.get("status") == "healthy"
    assert "version" in json_response
    assert isinstance(json_response.get("version"), str)

def test_process_text():
    version = get_version()  # Récupération dynamique de la version
    json_data = {"raw_text": RAW_TEXT}
    response = requests.post(f"{API_URL}/{version}/process-text", json=json_data)

    assert response.status_code == 200
    json_response = response.json()
    
    processed_text = json_response.get("processed_text")
    version_resp = json_response.get("version")

    assert isinstance(processed_text, str)
    assert processed_text != ""
    assert isinstance(version_resp, str)
