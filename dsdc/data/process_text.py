import re
import pandas as pd
import html
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import PunktSentenceTokenizer
nltk.download('punkt_tab')
# Télécharger les ressources NLTK nécessaires
nltk.download('stopwords')
nltk.download('punkt')

from dsdc.db.crud.processed_texts import get_missing_processed_text_raw_texts, add_processed_texts

from tqdm import tqdm

STOP_WORDS = set(stopwords.words('english'))
PG_REGEX = re.compile(r'pgNbr=[0-9]+')
PROCESSING_VERSION = "Text-processor v1.0.0"

def process_text(text):
    if text:
        # suppression paPgNbr:
        text = PG_REGEX.sub('', text)
        # unescape html
        text = html.unescape(text)
        # remove special_caracters
        text = text.lower()
        # Attention, c'est brutal, ca supprime tous les chiffres aussi...
        word_regex = re.compile(r'[a-z]{2,}')
        text = ' '.join(word_regex.findall(text))

        words = word_tokenize(text.lower())
        filtered = [word for word in words if word.isalpha() and word not in STOP_WORDS]
        text = " ".join(filtered)
    return text
    # jamspell_model_path = PATHS.models / 'jamspell' / 'en.bin'
    # assert jamspell_model_path.exists()
    # jamspell_model_path = str(jamspell_model_path)
    # corrector = jamspell.TSpellCorrector()
    # corrector.LoadLangModel(jamspell_model_path)
    # def apply_jamspell(text):
    #     if not text:
    #         return text
    #     return corrector.FixFragment(text)

    # t0 = time.time()
    # df.loc[:,"ocr_tmp"] = df.ocr_tmp.apply(apply_jamspell)



if __name__ == '__main__':
    raw_texts = get_missing_processed_text_raw_texts()
    logging.info(f"processing text from {len(raw_texts)} documents with {PROCESSING_VERSION}")
    raw_text_ids, processed_texts, versions = [], [], []
    for raw_text in tqdm(raw_texts):
        processed_text = process_text(raw_text.raw_text)
        raw_text_ids.append(raw_text.id)
        processed_texts.append(processed_text)
        versions.append(PROCESSING_VERSION)
    add_processed_texts(zip(
        raw_text_ids,
        processed_texts,
        versions
    ))
    logging.info(f"Successfully added {len(raw_texts)} documents inside raw_texts table")