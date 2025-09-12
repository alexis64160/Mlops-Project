import logging
from pathlib import Path
from typing import Union

from dsdc.db import SessionLocal
from dsdc.db.models import ProcessedImage


def get_processed_image_list():
    session = SessionLocal()
    try:
        images = session.query(ProcessedImage).all()
    except Exception as e:
        logging.error(e)
    finally:
        session.close()
    return images

def add_preprocessed_image(document_id: str, file_path: Path|str, processor:str):
    session = SessionLocal()
    try:
        image = ProcessedImage(
            document_id=document_id,
            image_file=file_path,
            processor=processor
            )
        session.add(image)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(e)
    finally:
        session.close()

def add_processed_images(images: list[tuple[str, Union[str, Path], str]]):
    """
    Import multiple documents and associated labels in one transaction.

    Args:
        images: List of tuples (document_id, processed_image_file_path, processor_name)
    """
    session = SessionLocal()
    try:
        image_objects = []

        for document_id, image_file, processor_name in images:
            image = ProcessedImage(document_id = document_id, image_file = str(image_file), processor=processor_name)
            image_objects.append(image)

        session.add_all(image_objects)
        session.commit()
        logging.info(f"Imported {len(image_objects)} processed images in database.")
    except Exception as e:
        session.rollback()
        logging.error(f"Batch import failed: {e}")
    finally:
        session.close()

