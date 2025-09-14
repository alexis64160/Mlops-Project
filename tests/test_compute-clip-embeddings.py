import pytest
import requests
import os

from dsdc import PROJECT_ROOT
API_URL = "http://localhost:8000"  # Change selon ton endpoint réel
TEST_IMAGE = PROJECT_ROOT/"tests"/"images"/"processed_image.png"
TEST_TEXT = "i will survive"

def test_compute_embeddings():
    if not os.path.exists(TEST_IMAGE):
        pytest.skip(f"Le fichier {TEST_IMAGE} n'existe pas, test ignoré.")

    with open(TEST_IMAGE, "rb") as f:
        files = {"image": (TEST_IMAGE.name, f, "image/png")}
        data = {"text": TEST_TEXT}
        response = requests.post(f"{API_URL}/compute-embeddings", files=files, data=data)
    assert response.status_code == 200
    json_response = response.json()
    embeddings = json_response.get("embeddings")
    assert isinstance(embeddings, list)
    assert all([isinstance(e, float) for e in embeddings])
    assert len(embeddings) == 1024
    version = json_response.get("version")
    assert isinstance(version, str)