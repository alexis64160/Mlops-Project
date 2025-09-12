import logging
from pathlib import Path
from typing import Union

from dsdc.db import SessionLocal
from dsdc.db.models import OriginalDocument

def get_document_lists():
    session = SessionLocal()
    try:
        images = session.query(OriginalDocument).all()
    except Exception as e:
        logging.error(e)
    finally:
        session.close()
    return images
