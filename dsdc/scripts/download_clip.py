import os
import requests

from dsdc import CONFIG

BASE_URL = "https://huggingface.co/openai/clip-vit-base-patch32/resolve/main"
DEST_DIR = CONFIG.paths.clip_model
DEST_DIR.mkdir(exist_ok=True, parents=True)

FILES = [
    "config.json",
    "pytorch_model.bin",
    "preprocessor_config.json",
    "tokenizer_config.json",
    "merges.txt",
    "vocab.json",
    "special_tokens_map.json"
]

def download_file(url: str, dest_path: str):
    print(f"⬇️  Téléchargement de {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Enregistré dans {dest_path}")
    else:
        print(f"❌ Échec du téléchargement : {url} (HTTP {response.status_code})")
        response.raise_for_status()

# 🔁 Télécharger tous les fichiers
for filename in FILES:
    url = f"{BASE_URL}/{filename}"
    dest_path = os.path.join(DEST_DIR, filename)
    download_file(url, dest_path)

print("\n🎉 Tous les fichiers ont été téléchargés avec succès.")