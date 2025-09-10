import logging
from typing import Union

from dsdc.db import SessionLocal
from dsdc.db.models import OriginalDocument, Label
from pathlib import Path

def add_document_with_label(document_id: str, file_path: Path|str, label: int):
    session = SessionLocal()
    try:
        doc = OriginalDocument(id=document_id, original_file=str(file_path))
        label = Label(document_id=document_id, source="user", label=label)
        session.add(doc)
        session.add(label)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(e)
    finally:
        session.close()

def add_documents_with_labels(documents: list[tuple[str, Union[str, Path], int]]):
    """
    Import multiple documents and associated labels in one transaction.

    Args:
        docs: List of tuples (document_id, file_path, label)
        source: Source of the labels (default: 'batch')
    """
    session = SessionLocal()
    try:
        doc_objects = []
        label_objects = []

        for document_id, file_path, label_value in documents:
            doc = OriginalDocument(id=document_id, original_file=str(file_path))
            label = Label(document_id=document_id, label=label_value)
            doc_objects.append(doc)
            label_objects.append(label)

        session.add_all(doc_objects)
        session.add_all(label_objects)
        session.commit()
        logging.info(f"Imported {len(doc_objects)} documents with labels.")
    except Exception as e:
        session.rollback()
        logging.error(f"Batch import failed: {e}")
    finally:
        session.close()

def get_document_list():
    session = SessionLocal()
    try:
        docs = session.query(OriginalDocument).all()
    except Exception as e:
        logging.error(e)
    finally:
        session.close()
    return docs

# from sqlalchemy.orm import joinedload

# def get_documents_with_labels():
#     session = SessionLocal()
#     try:
#         docs = session.query(OriginalDocument).options(joinedload(OriginalDocument.labels)).all()
#         for doc in docs:
#             print(f"Document {doc.id} has labels:")
#             for label in doc.labels:
#                 print(f"  - Label {label.label} (source: {label.source})")
#     finally:
#         session.close()

# def get_embeddings_for_document(document_id: str):
#     session = SessionLocal()
#     try:
#         embeddings = (
#             session.query(Embedding)
#             .join(Embedding.processed_image)
#             .join(ProcessedImage.document)
#             .filter(OriginalDocument.id == document_id)
#             .all()
#         )
#         for emb in embeddings:
#             print(f"Embedding ID {emb.id}, clip_version: {emb.clip_version}")
#     finally:
#         session.close()