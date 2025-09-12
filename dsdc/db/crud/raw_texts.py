from typing import List, Tuple

from dsdc.db import SessionLocal
from dsdc.db.models import RawText, OriginalDocument


def get_missing_raw_text_document_ids() -> List[str]:
    session = SessionLocal()
    try:
        # LEFT OUTER JOIN et filtre sur raw_text NULL
        result = (
            session.query(OriginalDocument.id)
            .outerjoin(RawText, RawText.document_id == OriginalDocument.id)
            .filter(RawText.id.is_(None))
            .all()
        )
        return [row[0] for row in result]
    finally:
        session.close()

def add_raw_text(document_id: str, raw_text: str, processor: str) -> None:
    session = SessionLocal()
    try:
        new_entry = RawText(
            document_id=document_id,
            raw_text=raw_text,
            processor=processor
        )
        session.add(new_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_raw_texts(batch: List[Tuple[str, str, str]]) -> None:
    session = SessionLocal()
    try:
        entries = [
            RawText(
                document_id=doc_id,
                raw_text=text,
                processor=processor,
            )
            for doc_id, text, processor in batch
        ]
        session.add_all(entries)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()