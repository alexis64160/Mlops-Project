import shutil
import logging
import pandas as pd

from dsdc import CONFIG
from dsdc.db.crud import add_documents_with_labels
from dsdc.utils.project_files import compute_document_id, compute_storage_path, get_processed_image_path, get_images_files_in_directory

def get_labels(original_file_paths):
    cdip_ids = [o.parent.name for o in original_file_paths]
    labels_df = pd.read_csv(CONFIG.paths.rvl_csv)
    labels = labels_df[labels_df["document_id"].isin(cdip_ids)][["document_id", "label"]].set_index("document_id").to_dict()['label']
    labels = [labels[d] for d in cdip_ids]

def move_files(original_file_paths, storage_file_paths):
    logging.info(f"Moving {len(original_file_paths)} files")
    for original_file_path, storage_file_path in zip(original_file_paths, storage_file_paths):
        shutil.move(original_file_path, storage_file_path)

if __name__ == "__main__":
    original_file_paths = get_images_files_in_directory(CONFIG.paths.to_ingest, absolute=True)
    logging.info(f"Preparing to ingest {len(original_file_paths)} documents")
    document_ids = list(map(compute_document_id, original_file_paths))
    storage_file_paths = list(map(compute_storage_path, original_file_paths, document_ids))
    preprocessed_image_paths = list(map(get_processed_image_path, document_ids))
    labels = list(map(get_labels, original_file_paths))

    # ecriture dans la table documents
    add_documents_with_labels(zip(document_ids, storage_file_paths, labels))
    # déplacement des fichiers
    move_files(original_file_paths, storage_file_paths)