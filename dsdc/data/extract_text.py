from PIL import Image
import pytesseract
import logging
from tqdm import tqdm

from dsdc.db.crud.raw_texts import get_missing_raw_text_document_ids, add_raw_texts
from dsdc.db.crud.original_documents import get_original_image_paths

try:
    version = str(pytesseract.get_tesseract_version())
    print("Tesseract version:", version)
    print("pytesseract est bien configuré.")
except Exception as e:
    print("Erreur:", e)
    logging.info("trying to set pytesseract path manually")
    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract" # Chemin à mettre à jour le cas echeant
    try:
        version = str(pytesseract.get_tesseract_version())
        print("Tesseract version:", version)
        print("pytesseract est bien configuré.")
    except Exception as e:
        print("Erreur:", e)
version = f"Tesseract v{version}"

def extract_text(image_file_path):
    try:
        # Ouvrir l'image avec PIL
        image = Image.open(image_file_path)

        # Utiliser pytesseract pour extraire le texte
        extracted_text = pytesseract.image_to_string(image, lang='eng')

        return extracted_text.strip(), version
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction du texte : {e}")
        return None, version

def extract_texts():
    document_ids = get_missing_raw_text_document_ids()
    image_paths = get_original_image_paths(document_ids)
    logging.info(f"extracting text from {len(document_ids)} documents with {version}")
    raw_texts, versions = [], []
    for image_path in tqdm(image_paths):
        raw_text, version = extract_text(image_file_path=image_path)
        raw_texts.append(raw_text)
        versions.append(version)
    add_raw_texts(zip(
        document_ids,
        raw_texts,
        versions
    ))
    logging.info(f"Successfully added {len(document_ids)} documents inside raw_texts table")
    
if __name__ == '__main__':
    extract_texts()
