import hashlib
from pathlib import Path
import os
from dsdc import CONFIG


def compute_document_id(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()

def compute_storage_path(original_file_path:Path, document_id:str):
    return CONFIG.paths.raw/document_id[0]/document_id[1]/f"{document_id}{original_file_path.suffix}"

def get_processed_image_path(document_id:str):
    return CONFIG.paths.processed/document_id[0]/document_id[1]/f"{document_id}.png"



def get_images_files_in_directory(directory, absolute=False):
    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
    file_paths = []
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        for filename in files:
            path = root_path/filename
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                file_paths.append(path)
    return file_paths

