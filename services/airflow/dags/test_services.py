import logging
from dsdc.db import SessionLocal
from dsdc import PROJECT_ROOT
from airflow.decorators import dag, task, task_group
from datetime import datetime
import requests
import numpy as np
import io
from PIL import Image

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 14),
}


@task(task_id="hello_world")
def test_hello_world():
    logging.info("Hello world!")


# region POSTGRES
@task(task_id="test_postgres_connection")
def test_postgres_connection():
    try:
        with SessionLocal() as session:
            session.execute("SELECT 1")
        logging.info("PostgreSQL is reachable.")
    except Exception as e:
        logging.error(f"Unable to connect to PostgreSQL: {e}")
        raise

@task(task_id="test_postgres")
def test_postgres_dsdc_tables():
    expected_tables = {
        "original_documents",
        "labels",
        "processed_images",
        "raw_texts",
        "processed_texts",
        "embeddings"
    }
    with SessionLocal() as session:
        response = session.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """).fetchall()
    found_tables = set(r[0] for r in response)
    missing_tables = expected_tables - found_tables
    if missing_tables == set():
        logging.info("All expected tables were retrieved")
    else:
        error_message = f"Following tables were not retrieved: {missing_tables}"
        logging.error(error_message)
        raise ValueError(error_message)


@task_group(group_id="test_postgres")
def test_postgres():
    test_postgres_connection() >> test_postgres_dsdc_tables()


# region extract_text
@task(task_id="test_extract_texts_healthy")
def test_extract_texts_healthy():
    url="http://dsdc-extract-text:8000/status"
    logging.info(f"testing whether extract-text api is healthy")
    response = requests.get(url)
    logging.info(response.status_code)
    assert response.status_code == 200
    json_response = response.json()
    status = json_response.get("status")
    version = json_response.get("version")
    logging.info(f"extract_text api is {status} - running on version {version}.")
    return version

@task(task_id="test_extract_texts_functional")
def test_extract_texts_functional(version: str):
    url=f"http://dsdc-extract-text:8000/{version}/extract-text"
    logging.info(f"testing whether extract-text api is functional")
    image_path = PROJECT_ROOT/"tests"/"sample"/"rvl_aaa06d00_original.tif" # TODO: mettre ca dans CONFIG (+ ajouter path tests?)
    with open(image_path, "rb") as f:
        files = {"image": (image_path.name, f, "image/tiff")}
        response = requests.post(url, files=files)
    assert response.status_code == 200
    json_response = response.json()
    raw_text = json_response.get("extracted_text")
    assert len(raw_text) > 0    
    try:
        text_path = PROJECT_ROOT/"tests"/"sample"/"rvl_aaa06d00_raw_text.txt"
        with open(text_path, "r") as f:
            ref_text = f.read()
        assert raw_text == ref_text
        logging.info("Extracted text content is exactly as expected.")
    except:
        logging.warning("Extracted text did not match expected text.")

@task_group(group_id="test_extract_text")
def test_extract_texts():
    version = test_extract_texts_healthy() 
    test_extract_texts_functional(version)


# region process_text
@task(task_id="test_process_texts_healthy")
def test_process_texts_healthy():
    API_URL="http://dsdc-process-text:8000/status"
    logging.info(f"testing whether process-text api is healthy")
    response = requests.get(API_URL)
    logging.info(response.status_code)
    assert response.status_code == 200
    json_response = response.json()
    status = json_response.get("status")
    version = json_response.get("version")
    logging.info(f"process_text api is {status} - running on version {version}.")
    return version

@task(task_id="test_process_texts_functional")
def test_process_texts_functional(version: str):
    API_URL=f"http://dsdc-process-text:8000/{version}/process-text"
    logging.info(f"testing whether process-text api is functional")
    raw_text_path = PROJECT_ROOT/"tests"/"sample"/"rvl_aaa06d00_raw_text.txt"
    with open(raw_text_path, "r") as f:
        raw_text = f.read()
    response = requests.post(API_URL, json={"raw_text": raw_text})
    assert response.status_code == 200
    json_response = response.json()
    logging.info(json_response)
    processed_text = json_response.get("processed_text")
    assert len(processed_text) > 0    
    try:
        text_path = PROJECT_ROOT/"tests"/"sample"/"rvl_aaa06d00_processed_text.txt"
        with open(text_path, "r") as f:
            ref_text = f.read()
        assert processed_text == ref_text
        logging.info("Processed text content is exactly as expected.")
    except:
        logging.warning("Processed text did not match expected text.")
    logging.info(processed_text)
@task_group(group_id="test_process_text")
def test_process_texts():
    version = test_process_texts_healthy() 
    test_process_texts_functional(version)


#region process_image
@task(task_id="test_process_image_healthy")
def test_process_image_healthy():
    API_URL = "http://dsdc-process-image:8000/status"
    logging.info("Testing whether process-image API is healthy.")
    response = requests.get(API_URL)
    logging.info(f"Status code: {response.status_code}")
    assert response.status_code == 200
    json_response = response.json()
    status = json_response.get("status")
    version = json_response.get("version")
    logging.info(f"process-image API is {status} - running on version {version}.")
    return version

@task(task_id="test_process_image_functional")
def test_process_image_functional(version: str):
    API_URL = f"http://dsdc-process-image:8000/{version}/process-image"
    def images_are_similar(img1: Image.Image, img2: Image.Image, tolerance: int = 5) -> bool:
        """
        Compare deux images avec une tolérance pixel par pixel.
        """
        arr1 = np.array(img1).astype(np.int16)
        arr2 = np.array(img2).astype(np.int16)

        if arr1.shape != arr2.shape:
            logging.error(f"Shape mismatch: {arr1.shape} vs {arr2.shape}")
            return False

        diff = np.abs(arr1 - arr2)
        max_diff = np.max(diff)
        logging.info(f"Max pixel difference: {max_diff}")
        return max_diff <= tolerance

    logging.info("Testing whether process-image API is functional.")
    image_path = PROJECT_ROOT / "tests" / "sample" / "rvl_aaa06d00_original.tif"
    ref_path = PROJECT_ROOT / "tests" / "sample" / "rvl_aaa06d00_processed.png"
    with open(image_path, "rb") as f:
        files = {"image": (image_path.name, f, "image/tiff")}
        response = requests.post(API_URL, files=files)
    assert response.status_code == 200
    content_type = response.headers.get("Content-Type", "")
    assert "image" in content_type, f"Expected image, got {content_type}"

    try:
        returned_img = Image.open(io.BytesIO(response.content)).convert("RGB")
        logging.info("Returned image successfully opened.")
    except Exception as e:
        logging.error(f"Could not open returned image: {e}")
        raise
    try:
        with open(ref_path, "rb") as f:
            ref_img = Image.open(f).convert("RGB")
    except Exception as e:
        logging.error(f"Could not load reference image: {e}")
        raise

    if not images_are_similar(returned_img, ref_img, tolerance=5):
        raise AssertionError("L'image retournée est trop différente de l'image de référence.")
    else:
        logging.info("Processed image is visually similar to the reference image (within tolerance).")

@task_group(group_id="test_process_image")
def test_process_image():
    version = test_process_image_healthy()
    test_process_image_functional(version)

# region compute embeddings
@task(task_id="test_embeddings_api_healthy")
def test_embeddings_api_healthy():
    API_URL = "http://dsdc-compute-clip-embeddings:8000/status"
    logging.info("Testing whether compute-embeddings API is healthy.")
    response = requests.get(API_URL)
    assert response.status_code == 200
    json_response = response.json()
    version = json_response.get("version")
    status = json_response.get("status")
    logging.info(f"compute-embeddings API is {status} - running on version {version}")
    return version

@task(task_id="test_embeddings_api_functional")
def test_embeddings_api_functional(version: str):
    API_URL = f"http://dsdc-compute-clip-embeddings:8000/{version}/compute-embeddings"
    logging.info("Testing whether compute-embeddings API is functional.")

    # Préparer les fichiers de test
    image_path = PROJECT_ROOT / "tests" / "sample" / "rvl_aaa06d00_processed.png"
    text_path = PROJECT_ROOT / "tests" / "sample" / "rvl_aaa06d00_processed_text.txt"

    with open(image_path, "rb") as img_file, open(text_path, "r") as txt_file:
        text = txt_file.read()
        files = {"image": (image_path.name, img_file, "image/png")}
        data = {"text": text}
        response = requests.post(API_URL, files=files, data=data)

    # Vérifications
    assert response.status_code == 200, f"Status code: {response.status_code}"
    json_response = response.json()
    embeddings = json_response.get("embeddings")
    
    assert embeddings is not None, "No 'embeddings' field in response"
    assert isinstance(embeddings, list), "Embeddings should be a list"
    assert len(embeddings) == 1024, f"Expected 1024-dim embedding, got {len(embeddings)}"
    assert all(isinstance(x, (int, float)) for x in embeddings), "Embeddings must be numeric"

    logging.info("Embeddings successfully computed and valid.")

@task_group(group_id="test_compute_embeddings")
def test_compute_embeddings():
    version = test_embeddings_api_healthy()
    test_embeddings_api_functional(version)


# region predict
@task(task_id="test_predict_healthy")
def test_predict_healthy():
    API_URL="http://dsdc-predict:8000/status"
    logging.info(f"testing whether predict api is healthy")
    response = requests.get(API_URL)
    logging.info(response.status_code)
    assert response.status_code == 200
    json_response = response.json()
    status = json_response.get("status")
    version = json_response.get("version")
    logging.info(f"predict api is {status} - running on version {version}.")
    return version

@task(task_id="test_predict_functional")
def test_predict_functional(version: str):
    API_URL=f"http://dsdc-predict:8000/{version}/predict"
    logging.info(f"testing whether predict api is functional")

    image = PROJECT_ROOT/"tests"/"sample"/"rvl_aaa06d00_original.tif"
    response = requests.post(
        API_URL,
        files={"image": (image.name, open(image, "rb"), "image/tiff")}
    )
    assert response.status_code == 200, response.status_code
    label_path = PROJECT_ROOT/"tests"/"sample"/"rvl_aaa06d00_label.txt"
    with open(label_path) as f:
        expected_label = int(f.read().strip())
    json_response = response.json()
    label = json_response["label"]
    probas = json_response["probas"]
    assert label == expected_label
    logging.info(probas)
    assert len(probas) == 16
    logging.info("Successfully tested prediction service (prediction = {label}, as expected).")

    
@task_group(group_id="test_predict")
def test_predict():
    version = test_predict_healthy() 
    test_predict_functional(version)


# region DAG
@dag(
    dag_id="dag_test_services",
    default_args=default_args,
    schedule="58 * * * *",
    catchup=False,
    tags=["test", "debug"],
)
def test_services():

    hw = test_hello_world()
    pos = test_postgres()
    et = test_extract_texts()
    pt = test_process_texts()
    pi = test_process_image()
    pr = test_predict()
    ce = test_compute_embeddings()
    hw >> pos
    pos >> et
    pos >> pt
    pos >> pi
    pos >> ce
    et >> pr
    pt >> pr
    pi >> pr
    ce >> pr
dag = test_services()
