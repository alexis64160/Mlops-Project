

import logging
from sqlalchemy import not_
from typing import List, Optional, Tuple, Union

from dsdc.db import SessionLocal
from dsdc.db.models import (
    OriginalDocument,
    ProcessedImage,
    RawText,
    ProcessedText,
    Embedding,
)

def get_missing_embeddings_document_ids() -> List[str]:
    session = SessionLocal()
    try:
        # Sous-requêtes pour récupérer les documents déjà utilisés dans des embeddings (texte ou image)
        embedded_image_doc_ids = (
            session.query(ProcessedImage.document_id)
            .join(Embedding, Embedding.processed_image_id == ProcessedImage.id)
            .distinct()
        )

        embedded_text_doc_ids = (
            session.query(RawText.document_id)
            .join(ProcessedText, ProcessedText.raw_text_id == RawText.id)
            .join(Embedding, Embedding.processed_text_id == ProcessedText.id)
            .distinct()
        )

        # Requête principale : documents avec image + texte traités, mais pas encore d'embedding
        result = (
            session.query(OriginalDocument.id)
            .join(ProcessedImage, ProcessedImage.document_id == OriginalDocument.id)
            .join(RawText, RawText.document_id == OriginalDocument.id)
            .join(ProcessedText, ProcessedText.raw_text_id == RawText.id)
            .filter(
                not_(OriginalDocument.id.in_(embedded_image_doc_ids)),
                not_(OriginalDocument.id.in_(embedded_text_doc_ids)),
            )
            .distinct()
            .all()
        )
        return [row[0] for row in result]
    finally:
        session.close()


def add_embeddings(
    embeddings_data: List[Tuple[Optional[int], Optional[int], Union[List[float], 'np.ndarray'], str]]
) -> None:
    """
    Insert a batch of embeddings into the database.

    Args:
        embeddings_data (List[Tuple[processed_image_id, processed_text_id, embedding]]): 
            Each tuple contains:
                - processed_image_id (int or None)
                - processed_text_id (int or None)
                - embedding (List[float] or np.ndarray of length 1024)

        clip_version (str): Version string of the CLIP model used.
    """
    session = SessionLocal()
    try:
        records = []
        for image_id, text_id, emb, version in embeddings_data:
            if len(emb) != 1024:
                raise ValueError(f"Embedding must have 1024 dimensions, got {len(emb)}")
            records.append(
                Embedding(
                    processed_image_id=image_id,
                    processed_text_id=text_id,
                    clip_version=version,
                    embeddings=emb
                )
            )

        session.bulk_save_objects(records)
        session.commit()

    except Exception as e:
        logging.error(f"Error inserting embeddings: {e}")
        session.rollback()
        raise
    finally:
        session.close()