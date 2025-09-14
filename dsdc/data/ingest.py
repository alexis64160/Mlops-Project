import shutil
import logging
import pandas as pd

from dsdc import CONFIG
from dsdc.db.crud.labels import add_labels
from dsdc.db.crud.original_documents import get_original_documents, add_original_documents
from dsdc.utils.project_files import compute_document_id, compute_storage_path, get_processed_image_path, get_images_files_in_directory

def get_labels(original_file_paths):
    labels = []
    for original_file_path in original_file_paths:
        file_dir = original_file_path.parent
        label_file = file_dir/"label.txt"
        if not label_file.exists():
            logging.warning(f"no label file found for {original_file_path}")
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

def reject_candidate(candidate_path):
    candidate_folder = candidate_path.parent
    rejected_folder = CONFIG.paths.rejected/candidate_path.parent.relative_to(CONFIG.paths.to_ingest)
    shutil.move(candidate_folder, rejected_folder)

def accept_candidate(original_document_path, raw_document_path):
    source = CONFIG.paths.to_ingest/original_document_path
    destination = CONFIG.paths.raw/raw_document_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source, destination)
    shutil.rmtree(source.parent)


def ingest_data():
    logging.info(f"Scanning for new images to ingest")
    candidates = []
    for folder in CONFIG.paths.to_ingest.iterdir():
        if folder.is_dir(): # avoid .DS_Store on mac
            images = sorted(get_images_files_in_directory(folder))
            if len(images) == 0:
                logging.warning(f"Folder {folder} does not contain any image. Consider removing it")
            else:
                candidates.append(images[0])  # only keeps the first image if a document is made of several
    logging.info(f"found {len(candidates)} images in to ingest")
    existing_documents = get_original_documents()
    existing_document_ids = [d.id for d in existing_documents]
    elected_document_ids, raw_document_paths, original_document_paths, labels = [], [], [], []
    for candidate in candidates:
        document_id = compute_document_id(candidate)

        # Check document_id unicity
        if document_id in existing_document_ids:
            candidate_rel_path = candidate.relative_to(CONFIG.paths.to_ingest)
            existing_rel_path = [d for d in existing_documents if d.id == document_id][0].file_path
            logging.warning(f"rejecting document {str(candidate_rel_path)}: document is identical to {str(existing_rel_path)} with sha1 {document_id}")
            reject_candidate(candidate)
            continue

        # Check label validity
        label_is_ok = False
        label_file = candidate.parent/"label.txt"
        if label_file.exists():
            with open(label_file, 'r') as f:
                content = f.read()
            if content.isnumeric():
                label = int(content)
                if 0 <= label <=15:
                    label_is_ok = True
                else:
                    logging.warning(f"rejecting document {str(candidate_rel_path)}: label value of {label} is outside [0-15] interval")
            else:
                logging.warning(f"rejecting document {str(candidate_rel_path)}: label.txt file cannot be parsed as an integer (content start = {content[:10]}")
        else:
            logging.warning(f"rejecting document {str(candidate_rel_path)}: no label.txt file found")
        if not label_is_ok:
            reject_candidate(candidate)
            continue

        # add candidate to elected ones
        elected_document_ids.append(document_id)
        raw_document_paths.append(compute_storage_path(candidate, document_id).relative_to(CONFIG.paths.raw))
        original_document_paths.append(candidate.relative_to(CONFIG.paths.to_ingest))
        labels.append(label)
    
    logging.info(f"Preparing to ingest {len(elected_document_ids)} documents")
    
    add_original_documents(list(zip(
        elected_document_ids,
        raw_document_paths,
        original_document_paths
    )))

    add_labels(list(zip(
        elected_document_ids,
        labels
    )))
    for original_document_path, raw_document_path in zip(original_document_paths, raw_document_paths):
        accept_candidate(original_document_path, raw_document_path)

    # check that to_ingest is empty
    nb_files = 0
    nb_folders = 0
    for p in CONFIG.paths.to_ingest.iterdir():
        if p.is_file():
            nb_files += 1
        elif p.is_dir():
            nb_folders += 1
    if nb_folders + nb_files > 0:
        logging.warning(f"Some files were not ingested and remain in {CONFIG.paths.to_ingest} folder ({nb_files} files + {nb_folders} folders)")
    
if __name__ == "__main__":
    ingest_data()