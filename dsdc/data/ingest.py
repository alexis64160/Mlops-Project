import shutil
import logging
import pandas as pd

from dsdc import CONFIG
from dsdc.db.crud.labels import add_documents_with_labels
from dsdc.utils.project_files import compute_document_id, compute_storage_path, get_processed_image_path, get_images_files_in_directory

def get_labels(original_file_paths):
    labels = []
    for original_file_path in original_file_paths:
        file_dir = original_file_path.parent
        label_file = file_dir/"label.txt"
        if not label_file.exists():
            logging.warn(f"no label file found for {original_file_path}")
            labels.append(None)
            continue
        with open(label_file, 'r') as f:
            label = int(f.read())
        labels.append(label)
    return labels

def move_files(original_file_paths, storage_file_paths):
    logging.info(f"Moving {len(original_file_paths)} files")
    for original_file_path, storage_file_path in zip(original_file_paths, storage_file_paths):
        storage_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(original_file_path, storage_file_path)

if __name__ == "__main__":
    # original_file_paths = get_images_files_in_directory(CONFIG.paths.to_ingest)
    # previous line deprecated because documents can be made of several pages (models dont accept that so far).
    # consequantly, only first page is kept (in alphabetic order)
    original_file_paths = [
        sorted(get_images_files_in_directory(folder))[0]
        for folder in CONFIG.paths.to_ingest.iterdir()
        if folder.is_dir()      # avoid .DS_Store
    ]
    logging.info(f"Preparing to ingest {len(original_file_paths)} documents")
    document_ids = list(map(compute_document_id, original_file_paths))
    storage_file_paths = list(map(compute_storage_path, original_file_paths, document_ids))
    processed_image_paths = list(map(get_processed_image_path, document_ids))
    labels = get_labels(original_file_paths)

    # ecriture dans la table documents
    add_documents_with_labels(zip(
        document_ids,
        map(lambda p: p.relative_to(CONFIG.paths.raw), storage_file_paths),
        labels
        ))
    # # déplacement des fichiers
    move_files(original_file_paths, storage_file_paths)
    for p in CONFIG.paths.to_ingest.iterdir():
        shutil.rmtree(p)