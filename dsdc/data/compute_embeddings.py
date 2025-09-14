import logging

from dsdc.db.crud.embeddings import get_missing_embeddings_document_ids, add_embeddings
from dsdc.models.clip import CLIPSingleton

from dsdc import CONFIG
from dsdc.db.crud.processed_images import get_processed_images
from dsdc.db.crud.processed_texts import get_processed_texts

model = CLIPSingleton()

CLIP_VERSION = model.version

def compute_embeddings():
    document_ids = get_missing_embeddings_document_ids()
    logging.info(f"computing embeddings from {len(document_ids)} documents with {CLIP_VERSION}")
    images = get_processed_images(document_ids=document_ids)
    texts = get_processed_texts(document_ids)
    assert len(texts) == len(images), f"Mismatch between number of images ({len(images)}) and texts ({len(texts)})"
    embeddings = model.get_embeddings(
        [CONFIG.paths.processed/image.image_file for image in images],
        [text.processed_text for text in texts]
    )
    add_embeddings(list(zip(
        [image.id for image in images],
        [text.id for text in texts],
        embeddings,
        [CLIP_VERSION] * len(images)
    )))
    logging.info(f"Successfully added {len(embeddings)} documents inside raw_texts table")

if __name__ == '__main__':
    compute_embeddings()