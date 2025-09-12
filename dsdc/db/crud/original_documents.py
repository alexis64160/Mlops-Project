import logging
from pathlib import Path
from typing import Union

from dsdc import CONFIG
from dsdc.db import SessionLocal
from dsdc.db.models import OriginalDocument

def get_documents():
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
        query = session.query(OriginalDocument.id, OriginalDocument.original_file)
        
        if document_ids is not None:
            query = query.filter(OriginalDocument.id.in_(document_ids))
        
        result = query.all()  # List of tuples: [(id, original_file), ...]

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
        
# DEPRECATED (Ne garantit pas de conserver l'ordre)
# def get_original_image_paths(document_ids=None):
#     """
#     Retrieve the original file paths of documents from the database.

#     """
#     session = SessionLocal()
#     try:
#         query = session.query(OriginalDocument.original_file)
        
#         if document_ids is not None:
#             query = query.filter(OriginalDocument.id.in_(document_ids))
        
#         result = query.all()
        
#         # result is a list of single-element tuples: [(file1,), (file2,), ...]
#         return [CONFIG.paths.raw/row[0] for row in result]

#     except Exception as e:
#         logging.error(f"Error fetching original image paths: {e}")
#         return []
#     finally:
#         session.close()