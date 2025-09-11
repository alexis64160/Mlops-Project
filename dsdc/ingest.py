import os
from dsdc import CONFIG
import hashlib
import shutil
from pathlib import Path
import pandas as pd

from dsdc.image.preprocess import preprocess
from dsdc.image.preprocess import PREPROCESSOR_NAME as IMG_PREPROCESSOR_NAME

from dsdc.db.crud import add_preprocessed_image

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
def list_all_files(directory, absolute=False):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        for filename in files:
            path = root_path/filename
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                file_paths.append(path)
    return file_paths

original_file_paths = list_all_files(CONFIG.paths.to_ingest, absolute=True)
document_ids = list(map(get_sha1, original_file_paths))
storage_file_paths = list(map(get_storage_path, original_file_paths, document_ids))
preprocessed_image_paths = list(map(get_preprocessed_image_path, document_ids))

# for document_id, storage_file_path in zip(document_ids, storage_file_paths):
#     print(f"('{document_id}', '{str(storage_file_path.relative_to(CONFIG.paths.raw))}'),")
cdip_ids = [o.parent.name for o in original_file_paths]
labels_df = pd.read_csv(CONFIG.paths.rvl_csv)
labels = labels_df[labels_df["document_id"].isin(cdip_ids)][["document_id", "label"]].set_index("document_id").to_dict()['label']
labels = [labels[d] for d in cdip_ids]
for original_file_path, document_id, storage_file_path, preprocessed_image_path, label in \
        zip(original_file_paths, document_ids, storage_file_paths, preprocessed_image_paths, labels):
    add_label(document_id, label)
    preprocess(document_id, original_file_path, preprocessed_image_path)
    add_preprocessed_image(document_id, str(preprocessed_image_path.relative_to(CONFIG.paths.processed)), IMG_PREPROCESSOR_NAME)
    add_label(document_id, label)
    shutil.move(original_file_path, storage_file_path)