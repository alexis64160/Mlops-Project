import pytest
import requests
import os
import re

from dsdc import CONFIG
from dotenv import load_dotenv

load_dotenv(CONFIG.paths.project_root/"services"/".env")

API_URL = f"http://localhost:{os.environ['DSDC_EXTRACT_TEXT_PORT']}"
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
    version = json_response.get("version")
    assert isinstance(version, str)
    # Exemple de vérification format version x.y.z
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, version), f"Version {version} ne respecte pas le format x.y.z"

def test_extract_text():
    if not os.path.exists(TEST_IMAGE):
        pytest.skip(f"Le fichier {TEST_IMAGE} n'existe pas, test ignoré.")

    version = get_version()

    with open(TEST_IMAGE, "rb") as f:
        files = {"image": (TEST_IMAGE.name, f, "image/tiff")}
        response = requests.post(f"{API_URL}/{version}/extract-text", files=files)

    assert response.status_code == 200

    json_response = response.json()

    text = json_response.get("extracted_text")
    version_resp = json_response.get("version", version)  # Attention dans ton code API, la version n'est pas renvoyée, on en parle ci-dessous

    assert isinstance(text, str)
    assert len(text.strip()) > 0
    assert isinstance(version_resp, str)

    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, version_resp), f"Version {version_resp} ne respecte pas le format x.y.z"
