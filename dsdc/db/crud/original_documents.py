import logging
from pathlib import Path
from typing import Union, List

from dsdc import CONFIG
from dsdc.db import SessionLocal
from dsdc.db.models import OriginalDocument

def get_original_documents():
    session = SessionLocal()
    try:
        images = session.query(OriginalDocument).all()
    except Exception as e:
        logging.error(e)
    finally:
        session.close()
    return images


def get_original_image_paths(document_ids=None):
    """
    Retrieve the original file paths of documents from the database,
    preserving the input order of document_ids if provided.
    If a list of document IDs is provided, only those documents will be queried.
    Otherwise, all documents in the original_documents table are included.

    Returns:
        List[Path]: A list of file paths as pathlib.Path objects.
    """
    session = SessionLocal()
    try:
        query = session.query(OriginalDocument.id, OriginalDocument.file_path)
        
        if document_ids is not None:
            query = query.filter(OriginalDocument.id.in_(document_ids))
        
        result = query.all()  # List of tuples: [(id, file_path), ...]

        if document_ids is not None:
            # Convert to dict for fast lookup
            file_map = {doc_id: Path(CONFIG.paths.raw) / file for doc_id, file in result}
            return [file_map[doc_id] for doc_id in document_ids if doc_id in file_map]
        else:
            return [Path(CONFIG.paths.raw) / file for _, file in result]

    except Exception as e:
        logging.error(f"Error fetching original image paths: {e}")
        return []
    finally:
        session.close()

def add_original_documents(original_documents: List[tuple[str, Union[str, Path], Union[str, Path]]]):
    """
    Import multiple original documents in one transaction.
    Args:
        documents: List of tuples (document_id, raw_document_path, original_document_path)
            raw_document_path is relative to CONFIG.paths.data/raw
            original_document is relative to CONFIG.paths.data/to_ingest
    """
    session = SessionLocal()
    try:
        to_add = []
        for document_id, raw_document_path, original_document_path in original_documents:
            original_document = OriginalDocument(
                id=document_id,
                file_path=str(raw_document_path),
                original_name=str(original_document_path)
                )
            to_add.append(original_document)
        session.add_all(to_add)
        session.commit()
        logging.info(f"Successfully added {len(original_documents)} documents to original_document table.")
    except Exception as e:
        session.rollback()
        logging.error(f"Batch import failed: {e}")
    finally:
        session.close()
