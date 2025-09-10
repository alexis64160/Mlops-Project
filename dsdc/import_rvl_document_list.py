import csv
import requests
import logging
from pathlib import Path
from dsdc import PROJECT_ROOT, CONFIG

rvl_cdip_urls = {
    "train": "https://huggingface.co/datasets/rvl_cdip/resolve/main/data/train.txt",
    "test": "https://huggingface.co/datasets/rvl_cdip/resolve/main/data/test.txt",
    "val": "https://huggingface.co/datasets/rvl_cdip/resolve/main/data/val.txt",
}


def build_rvl_csv(csv_file=PROJECT_ROOT / CONFIG.paths.rvl_csv):
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
    build_rvl_csv()