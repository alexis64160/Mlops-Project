import logging
from typing import List

from dsdc.db import SessionLocal
from dsdc.db.models import Label

def add_labels(labels: List[tuple[str, int]]):
    session = SessionLocal()
    try:
        to_add = []
        print(len(labels))
        print(labels[0])
        for document_id, label in labels:
            label = Label(document_id=document_id, label=label)
            to_add.append(label)
        session.add_all(to_add)
        session.commit()
        logging.info(f"Successfully added {len(labels)} labels to labels table.")

    except Exception as e:
        session.rollback()
        logging.error(e)
    finally:
        session.close()