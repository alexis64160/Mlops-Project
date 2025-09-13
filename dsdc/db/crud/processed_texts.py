from typing import List, Tuple, Optional
import logging
from dsdc.db import SessionLocal
from dsdc.db.models import ProcessedText, RawText, OriginalDocument


def get_missing_processed_text_raw_texts() -> List[str]:
    session = SessionLocal()
    try:
        # LEFT OUTER JOIN pour trouver les raw_texts sans processed_text
        result = (
            session.query(RawText)
            .outerjoin(ProcessedText, ProcessedText.raw_text_id == RawText.id)
            .filter(ProcessedText.id.is_(None))
            .all()
        )
        return result
    finally:
        session.close()

def get_processed_texts(
    document_ids: Optional[List[str]] = None,
    raw_text_ids: Optional[List[int]] = None
) -> List[ProcessedText]:
    if document_ids is not None and raw_text_ids is not None:
        raise NotImplementedError("Filtering by both document_ids and raw_text_ids is not supported yet.")
    session = SessionLocal()
    try:
        query = session.query(ProcessedText)
        if document_ids is not None:
            query = query.join(RawText, ProcessedText.raw_text_id == RawText.id) \
                         .join(OriginalDocument, RawText.document_id == OriginalDocument.id) \
                         .filter(OriginalDocument.id.in_(document_ids))
        elif raw_text_ids is not None:
            query = query.filter(ProcessedText.raw_text_id.in_(raw_text_ids))
        results = query.all()
        if document_ids is not None:
            mapping = {}
            for pt in results:
                mapping[pt.raw_text.document_id] = pt
            ordered_results = [mapping[doc_id] for doc_id in document_ids if doc_id in mapping]
            return ordered_results
        return results
    except Exception as e:
        logging.error(f"Error in get_processed_texts: {e}")
        return []
    finally:
        session.close()

def add_processed_text(raw_text_id: int, processed_text: str, processor: str) -> None:
    session = SessionLocal()
    try:
        new_entry = ProcessedText(
            raw_text_id=raw_text_id,
            processed_text=processed_text,
            processor=processor,
        )
        session.add(new_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_processed_texts(batch: List[Tuple[int, str, str]]) -> List[int]:
    """
    batch = List of tuples: (raw_text_id, processed_text, processor)
    Returns list of inserted processed_text IDs.
    """
    session = SessionLocal()
    try:
        entries = [
            ProcessedText(
                raw_text_id=raw_text_id,
                processed_text=processed_text,
                processor=processor,
            )
            for raw_text_id, processed_text, processor in batch
        ]
        session.add_all(entries)
        session.commit()
        return [entry.id for entry in entries]
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
