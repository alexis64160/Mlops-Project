import pytest
import requests
import os
import re

from dsdc import PROJECT_ROOT

API_URL = "http://localhost:64411"  # Adaptable si ton service tourne ailleurs
TEST_IMAGE = PROJECT_ROOT / "tests" / "images" / "rvl_aaa06d00_original.tif"  # à adapter à ton image test

def test_extract_text():
    if not os.path.exists(TEST_IMAGE):
        pytest.skip(f"Le fichier {TEST_IMAGE} n'existe pas, test ignoré.")

    with open(TEST_IMAGE, "rb") as f:
        files = {"image": (TEST_IMAGE.name, f, "image/tiff")}
        response = requests.post(f"{API_URL}/extract-text", files=files)

    assert response.status_code == 200

    json_response = response.json()

    text = json_response.get("extracted_text")
    version = json_response.get("version")

    assert isinstance(text, str)
    assert len(text.strip()) > 0
    assert isinstance(version, str)
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, version), f"Version {version} ne respecte pas le format x.y.z"
