import pytest
import requests
import os

from dsdc import CONFIG
from dotenv import load_dotenv

load_dotenv(CONFIG.paths.project_root/"services"/".env")

API_URL = f"http://localhost:{os.environ['DSDC_COMPUTE_CLIP_EMBEDDINGS_PORT']}"
TEST_IMAGE = CONFIG.paths.project_root / "tests" / "sample" / "rvl_aaa06d00_processed.png"  # À adapter
TEST_TEXT = "i will survive"

def get_version():
    response = requests.get(f"{API_URL}/status")
    response.raise_for_status()
    return response.json().get("version")

def test_status():
    response = requests.get(f"{API_URL}/status")
    assert response.status_code == 200
    json_response = response.json()

    assert json_response.get("status") == "healthy"
    version = json_response.get("version")
    assert isinstance(version, str)

def test_compute_embeddings():
    if not os.path.exists(TEST_IMAGE):
        pytest.skip(f"Le fichier {TEST_IMAGE} n'existe pas, test ignoré.")

    version = get_version()

    with open(TEST_IMAGE, "rb") as f:
        files = {"image": (TEST_IMAGE.name, f, "image/png")}
        data = {"text": TEST_TEXT}
        response = requests.post(f"{API_URL}/{version}/compute-embeddings", files=files, data=data)

    assert response.status_code == 200
    json_response = response.json()

    embeddings = json_response.get("embeddings")
    version_resp = json_response.get("version", version)  # fallback if missing

    assert isinstance(embeddings, list)
    assert all(isinstance(e, float) for e in embeddings)
    assert len(embeddings) == 1024

    assert isinstance(version_resp, str)
