import pytest
import requests
import os
from PIL import Image
import io

from dsdc import PROJECT_ROOT

API_URL = "http://localhost:64413"  # Change selon le port où tourne ton conteneur
TEST_IMAGE = PROJECT_ROOT / "tests" / "images" / "rvl_aaa06d00_original.tif"  # À adapter

def test_process_image():
    if not os.path.exists(TEST_IMAGE):
        pytest.skip(f"Le fichier {TEST_IMAGE} n'existe pas, test ignoré.")

    with open(TEST_IMAGE, "rb") as f:
        files = {"image": (TEST_IMAGE.name, f, "image/tiff")}
        response = requests.post(f"{API_URL}/process-image", files=files)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Lire l’image depuis la réponse
    image_bytes = io.BytesIO(response.content)
    processed_image = Image.open(image_bytes)

    # Vérifier les dimensions
    assert processed_image.size == (224, 224)
    assert processed_image.mode == "RGB"