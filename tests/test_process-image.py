import pytest
import requests
import os
from PIL import Image
import io

from dsdc import CONFIG
from dotenv import load_dotenv

load_dotenv(CONFIG.paths.project_root/"services"/".env")

API_URL = f"http://localhost:{os.environ['DSDC_PROCESS_IMAGE_PORT']}"
TEST_IMAGE = CONFIG.paths.project_root / "tests" / "sample" / "rvl_aaa06d00_original.tif"  # À adapter

def get_version():
    response = requests.get(f"{API_URL}/status")
    response.raise_for_status()
    return response.json().get("version")

def test_status():
    response = requests.get(f"{API_URL}/status")

    assert response.status_code == 200
    json_response = response.json()

    assert json_response.get("status") == "healthy"
    assert "version" in json_response
    assert isinstance(json_response.get("version"), str)

def test_process_image():
    if not os.path.exists(TEST_IMAGE):
        pytest.skip(f"Le fichier {TEST_IMAGE} n'existe pas, test ignoré.")

    version = get_version()  # Récupération dynamique de la version

    with open(TEST_IMAGE, "rb") as f:
        files = {"image": (TEST_IMAGE.name, f, "image/tiff")}
        response = requests.post(f"{API_URL}/{version}/process-image", files=files)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Lire l’image depuis la réponse
    image_bytes = io.BytesIO(response.content)
    processed_image = Image.open(image_bytes)

    # Vérifier les dimensions
    assert processed_image.size == (224, 224)
    assert processed_image.mode == "RGB"
