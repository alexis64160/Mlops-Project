import os
import logging
from PIL import Image
from pathlib import Path

from dsdc import CONFIG
from dsdc.db.crud.original_documents import get_documents
from dsdc.db.crud.processed_images import get_processed_images, add_processed_images

_VERSION = "1.0.0"
_KIND = "pil_based"
PROCESSOR_NAME = f"{_KIND}_{_VERSION}"

def process(document_id, input_path:Path, output_path:Path):
    image = Image.open(input_path).convert("RGB")

    # Redimensionner plus grand pour pouvoir cropper ensuite (comme CLIP)
    # CLIP resize à 224 avec bicubic puis crop central à 224x224 → donc on va simuler ça
    # Comme on veut du 224x224 final, on resize directement
    image = image.resize((224, 224), resample=Image.BICUBIC)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

if __name__ == "__main__":
    documents = get_documents()
    document_ids = set(map(lambda x:x.id, documents))
    processed_images = get_processed_images()
    # TODO: Ajouter le processeur dans la requete (si le calcul a été fait avec un processeur plus ancien, 
    # on pourra souhaiter refaire le calcul)
    processed_image_ids = set(map(lambda x:x.document_id, processed_images))
    to_process = sorted(list(document_ids - processed_image_ids))
    
    documents = [d for d in documents if d.id in to_process]
    document_ids = list(map(
        lambda x: x.id,
        documents
    ))
    original_files = list(map(
        lambda x:CONFIG.paths.raw/x.original_file,
        documents
        ))

    output_paths = list(map(
        lambda doc: CONFIG.paths.processed/doc.id[0]/doc.id[1]/doc.id/"image.png",
        documents
    ))

    for document_id, original_file, output_path in zip(document_ids, original_files, output_paths):
        process(document_id, original_file, output_path)
    logging.info(f"{len(document_ids)} images were successfully processed.")
    add_processed_images(list(zip(
            document_ids,
            list(map(lambda p:p.relative_to(CONFIG.paths.processed), output_paths)),
            [PROCESSOR_NAME] * len(document_ids)
        )))
