import csv
import requests
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import time
import tarfile
import io
from tqdm import tqdm
import os
import random

from dsdc import CONFIG
from dsdc.db.crud import get_document_list, add_documents_with_labels


def pull_cdip_images(minimum_quantity = 500):

    rvl_documents = pd.read_csv(CONFIG.paths.rvl_csv)
    already_downloaded = set(d.id for d in get_document_list())
    not_downloaded = rvl_documents[~rvl_documents.document_id.isin(already_downloaded)]
    not_downloaded["prefix"] = not_downloaded.document_id.str.slice(0,2)
    not_downloaded_prefixes = not_downloaded["prefix"].unique().tolist()
    prefixes = []
    to_download = []
    while len(to_download) < minimum_quantity:
        prefix = random.choice(not_downloaded_prefixes)
        not_downloaded_prefixes.remove(prefix)
        to_download += not_downloaded[not_downloaded.prefix==prefix][["document_id", "label"]].values.tolist()
        prefixes.append(prefix)
    document_ids, labels = zip(*to_download)
    nist_images_base_url = "https://data.nist.gov/od/ds/ark:/88434/mds2-2531/cdip-images/"
    urls = [
        f"{nist_images_base_url}images.{prefix[0]}.{prefix[1]}.tar" for prefix in prefixes
    ]
    for url in urls:
        t = time.time()
        tif_amount = 0
        # Téléchargement avec progress bar
        logging.info(msg=f"téléchargement d'images depuis {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('Content-Length', 0))
        chunk_size = 1024 * 1024  # 1 MB
        temp_bytes = io.BytesIO()
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading .tar") as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                temp_bytes.write(chunk)
                pbar.update(len(chunk))
        temp_bytes.seek(0)
        response = requests.get(url, stream=True)
        response.raise_for_status()  # En cas d'erreur HTTP
        file_paths = {}
        with tarfile.open(fileobj=io.BytesIO(response.content), mode="r|*") as archive:
            for file in archive:
                if file.name.endswith('.tif'): # to filter xml files that are part of the archive
                    cdip_document_id, filename = file.name.split(os.sep)[4:]
                    if cdip_document_id in document_ids:
                        archive.extract(file, path=CONFIG.paths.to_ingest/cdip_document_id/filename)
                        file_paths[cdip_document_id] = f"{cdip_document_id}/{filename}"
                        tif_amount += 1
        logging.info(f"   ... Successfully imported {tif_amount} tif files, in {time.time() - t:.2f} seconds")
        logging.info(f"Adding data to postgres database")
        documents = [[document_id, file_paths[document_id], label] for document_id, label in zip(document_ids, labels)]
        add_documents_with_labels(documents)
        logging.info(f"Done")


def build_rvl_csv(csv_file=CONFIG.paths.rvl_csv):
    rvl_cdip_urls = {
        "train": "https://huggingface.co/datasets/rvl_cdip/resolve/main/data/train.txt",
        "test": "https://huggingface.co/datasets/rvl_cdip/resolve/main/data/test.txt",
        "val": "https://huggingface.co/datasets/rvl_cdip/resolve/main/data/val.txt",
    }
    all_entries = []

    for url in rvl_cdip_urls.values():
        logging.info(msg=f"retrieving data from {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while requesting {url}: {e}")
            continue

        lines = response.text.strip().split("\n")
        for line in lines:
            raw_path, label = line.strip().split()            
            # Supprimer les 4 premiers niveaux de répertoire
            parts = Path(raw_path).parts
            if len(parts) < 5:
                logging.warning(f"Invalid path format: {raw_path}")
                continue

            doc_folder = parts[4]  # 5e élément (index 4)
            filename = parts[-1]   # le fichier .tif
            all_entries.append((doc_folder, filename, label))

    # Tri alphabétique : d'abord par dossier, puis par nom de fichier
    all_entries.sort()

    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["document_id", "filename", "label"])
        writer.writerows(all_entries)

if __name__ == "__main__":
    if not CONFIG.paths.rvl_csv.exists():
        build_rvl_csv()
    pull_cdip_images()
