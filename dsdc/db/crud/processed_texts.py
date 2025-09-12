from typing import List, Tuple

from dsdc.db import SessionLocal
from dsdc.db.models import ProcessedText, RawText

def get_missing_processed_text_raw_text_ids() -> List[int]:
    session = SessionLocal()
    try:
        result = (
            session.query(RawText.id)
            .outerjoin(ProcessedText, ProcessedText.raw_text_id == RawText.id)
            .filter(ProcessedText.id.is_(None))
            .all()
        )
        return [row[0] for row in result]
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
        