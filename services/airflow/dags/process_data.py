from airflow.decorators import dag, task
from datetime import datetime
import logging
import requests

from dsdc import CONFIG
from dsdc.data.ingest import ingest_data
from dsdc.db.crud.original_documents import get_original_image_paths
from dsdc.db.crud.raw_texts import get_missing_raw_text_document_ids, add_raw_texts
from dsdc.db.crud.processed_texts import get_missing_processed_text_raw_texts, add_processed_texts, get_processed_texts
from dsdc.db.crud.processed_images import get_missing_processed_image_documents, add_processed_images, get_processed_images
from dsdc.db.crud.embeddings import get_missing_embeddings_document_ids, add_embeddings

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}
BATCH_SIZE = 100

@dag(
    dag_id="ingest_and_process_data",
    default_args=default_args,
    schedule="3/5 * * * *",  # schedule_interval est déprécié, utiliser schedule
    catchup=False,
    description="Ingest and process data",
    tags=["dsdc", "ingest", "process", "data"],
    max_active_runs=1,
)

def dag_ingest_and_process_data():
    @task(task_id="ingest_data")
    def task_ingest_data():
        batch_size = globals().get("BATCH_SIZE")
        ingest_data(batch_size = batch_size)
    
    @task(task_id="extract_texts")
    def task_extract_texts():
        API_URL="http://dsdc_extract_text:8000/extract-text"
        document_ids = get_missing_raw_text_document_ids()[:BATCH_SIZE]
        if not document_ids:
            logging.warning("No text to extract")
            return
        image_paths = get_original_image_paths(document_ids)
        logging.info(f"extracting text from {len(document_ids)} documents")
        raw_texts, versions = [], []
        for image_path in image_paths:
            with open(image_path, "rb") as f:
                files = {"image": (image_path.name, f, "image/tiff")}
                response = requests.post(API_URL, files=files)
            json_response = response.json()
            raw_text = json_response.get("extracted_text")
            version = json_response.get("version")
            raw_texts.append(raw_text)
            versions.append(version)
        add_raw_texts(zip(
            document_ids,
            raw_texts,
            versions
        ))
        logging.info(f"Successfully added {len(document_ids)} documents inside raw_texts table")

    @task(task_id="process_texts")
    def task_process_texts():
        API_URL="http://dsdc_process_text:8000/process-text"
        raw_texts = get_missing_processed_text_raw_texts()[:BATCH_SIZE]
        if not raw_texts:
            logging.warning("No raw text to process")
            return
        logging.info(f"processing text from {len(raw_texts)} documents")
        raw_text_ids, processed_texts, versions = [], [], []
        for raw_text in raw_texts:
            json_data = {"raw_text": raw_text.raw_text}
            response = requests.post(API_URL, json=json_data)
            json_response = response.json()
            processed_text = json_response.get("processed_text")
            version = json_response.get("version")
            raw_text_ids.append(raw_text.id)
            processed_texts.append(processed_text)
            versions.append(version)
        add_processed_texts(zip(
            raw_text_ids,
            processed_texts,
            versions
        ))
        logging.info(f"Successfully added {len(raw_texts)} documents inside raw_texts table")

    @task(task_id="process_images")
    def task_process_images():
        API_URL="http://dsdc_process_image:8000/process-image"
        documents = get_missing_processed_image_documents()[:BATCH_SIZE]
        if not documents:
            logging.warning("No image to process")
            return
        logging.info(f"processing {len(documents)} images")
        raw_paths = [CONFIG.paths.raw/document.file_path for document in documents]
        document_ids = [document.id for document in documents]
        processed_paths, versions = [], []
        for document_id, raw_path in zip(document_ids, raw_paths):
            with open(raw_path, "rb") as f:
                files = {"image": (raw_path.name, f, "image/tiff")}
                response = requests.post(API_URL, files=files)
            processed_path = CONFIG.paths.processed/document_id[0]/document_id[1]/document_id/"image.png"
            processed_path.parent.mkdir(exist_ok=True, parents=True)
            with open(processed_path, "wb") as f:
                f.write(response.content)
            processed_paths.append(processed_path)
            version="0.0.0" #TODO
            versions.append(version)
        add_processed_images(zip(
            document_ids,
            processed_paths,
            versions
        ))
        logging.info(f"Successfully added {len(document_ids)} documents inside processed_images table")

    @task(task_id="compute_embeddings")
    def task_compute_embeddings():
        API_URL="http://dsdc_compute_clip_embeddings:8000/compute-embeddings"
        document_ids=get_missing_embeddings_document_ids()[:BATCH_SIZE]
        texts = get_processed_texts(document_ids=document_ids) # function keeps order
        images = get_processed_images(document_ids=document_ids) # function keeps order
        embeddings, processed_image_ids, processed_text_ids, versions = [], [], [], []
        for text, image in zip(texts, images):
            image_path = CONFIG.paths.processed/image.image_file
            with open(image_path, "rb") as f:
                files = {"image": (image_path.name, f, "image/png")}
                data = {"text": text.processed_text}
                response = requests.post(API_URL, files=files, data=data)
            json_response = response.json()
            embeddings = json_response.get("embeddings")
            version = "0.0.0" # TODO
            versions.append(version)
        add_embeddings(embeddings_data=zip(
                embeddings,
                processed_image_ids,
                processed_text_ids,
                versions
                ))
        logging.info(f"Successfully added {len(document_ids)} rows inside embeddings table")
    
    ingest = task_ingest_data() 
    extract_text = task_extract_texts()
    process_text = task_process_texts()
    process_image = task_process_images()
    compute_embeddings = task_compute_embeddings()
    ingest >> extract_text 
    ingest >> process_image
    extract_text >> process_text
    process_text >> compute_embeddings
    process_image >> compute_embeddings

dag = dag_ingest_and_process_data()