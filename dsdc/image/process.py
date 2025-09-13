from PIL import Image
import os
import logging
from pathlib import Path
from dsdc.db.crud.processed_images import add_preprocessed_image

_VERSION = "1.0.0"
_KIND = "pil_based"
PREPROCESSOR_NAME = f"{_KIND}_{_VERSION}"

def process(document_id, input_path:Path, output_path:Path):
    image = Image.open(input_path).convert("RGB")

    # Redimensionner plus grand pour pouvoir cropper ensuite (comme CLIP)
    # CLIP resize à 224 avec bicubic puis crop central à 224x224 → donc on va simuler ça
    # Comme on veut du 224x224 final, on resize directement
    image = image.resize((224, 224), resample=Image.BICUBIC)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

