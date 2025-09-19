import pytest
import requests

API_URL = "http://localhost:64412"
RAW_TEXT = "This is some sample raw text to process."

def test_process_text():
    json_data = {"raw_text": RAW_TEXT}
    response = requests.post(f"{API_URL}/process-text", json=json_data)

    assert response.status_code == 200
    json_response = response.json()
    
    processed_text = json_response.get("processed_text")
    version = json_response.get("version")

    assert isinstance(processed_text, str)
    assert processed_text != ""
    assert isinstance(version, str)