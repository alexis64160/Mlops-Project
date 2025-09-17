import csv
import requests
import logging
from pathlib import Path
import pandas as pd
import time
import tarfile
import io
from tqdm import tqdm
import os
import random
import shutil
from dsdc import CONFIG
from dsdc.db.crud.original_documents import get_original_documents
from dsdc.utils.project_files import get_images_files_in_directory

def pull_cdip_images(minimum_quantity = 500):

    rvl_documents = pd.read_csv(CONFIG.paths.rvl_csv)
    already_downloaded = set(d.id for d in get_original_documents())
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
    logging.info(f"preparing to add {len(document_ids)} documents (letters {prefix})")
    # TODO: intégrer un fichier label dans to_ingest (le fichier rvl ne devrait plus servir dans import)

    if CONFIG.settings.primarly_use_alternative_cdip_images:
        # copie des images depuis un répertoire local
        logging.info(f"Looking for files in local repository {CONFIG.paths.alternative_cdip_images}")
        t = time.time()
        tif_amount = 0
        paths = [CONFIG.paths.alternative_cdip_images/f"images{prefix[0]}"/prefix[0]/prefix[1] for prefix in prefixes]
        for source_file in sum(list(map(get_images_files_in_directory, paths)), []):
            cdip_document_id = source_file.parent.name
            filename = source_file.name
            dest_dir = CONFIG.paths.to_ingest / cdip_document_id
            dest_dir.mkdir(exist_ok=True, parents=True)
            dest_file = dest_dir / filename
            shutil.copy(source_file, dest_file)
            label = int(rvl_documents.loc[rvl_documents.document_id==cdip_document_id,"label"].values[0])
            with open(dest_dir/"label.txt", "w") as f:
                f.write(str(label))
            tif_amount += 1
        logging.info(f"   ... Successfully imported {tif_amount} tif files, in {time.time() - t:.2f} seconds")

    else:
        # téléchargement des images
        logging.info("Downloading images from nist.gov")
        nist_images_base_url = "https://data.nist.gov/od/ds/ark:/88434/mds2-2531/cdip-images/"
        urls = [
            f"{nist_images_base_url}images.{prefix[0]}.{prefix[1]}.tar" for prefix in prefixes
        ]
        for url in urls:
            t = time.time()
            tif_amount = 0
            logging.info(msg=f"téléchargement d'images depuis {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            file_paths = {}
            tif_amount = 0
            with tarfile.open(fileobj=io.BytesIO(response.content), mode="r|*") as archive:
                for file in archive:
                    if file.name.endswith('.tif'):
                        cdip_document_id, filename = file.name.split(os.sep)[4:]
                        if cdip_document_id in document_ids:
                            dest_dir = CONFIG.paths.to_ingest / cdip_document_id
                            dest_dir.mkdir(parents=True, exist_ok=True)
                            dest_path = dest_dir / filename
                            extracted_file = archive.extractfile(file)
                            if extracted_file:
                                with open(dest_path, 'wb') as out_f:
                                    shutil.copyfileobj(extracted_file, out_f)
                                file_paths[cdip_document_id] = f"{cdip_document_id}/{filename}"
                                label = int(rvl_documents.loc[rvl_documents.document_id==cdip_document_id,"label"].values[0])
                                with open(dest_dir/"label.txt", "w") as f:
                                    f.write(str(label))
                                tif_amount += 1        
            logging.info(f"   ... Successfully imported {tif_amount} tif files, in {time.time() - t:.2f} seconds")
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
