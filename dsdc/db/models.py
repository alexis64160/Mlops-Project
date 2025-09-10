from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, Text, Float, ARRAY
from sqlalchemy.orm import relationship
from dsdc.db import Base

class OriginalDocument(Base):
    __tablename__ = 'original_documents'
    
    id = Column(String, primary_key=True)
    original_file = Column(String, nullable=False)
    import_datetime = Column(TIMESTAMP)

    labels = relationship("Label", back_populates="document")
    processed_images = relationship("ProcessedImage", back_populates="document")
    raw_texts = relationship("RawText", back_populates="document")


class Label(Base):
    __tablename__ = 'labels'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(String, ForeignKey("original_documents.id"))
    source = Column(String)
    label = Column(Integer, nullable=False)

    document = relationship("OriginalDocument", back_populates="labels")


class ProcessedImage(Base):
    __tablename__ = 'processed_images'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(String, ForeignKey("original_documents.id"))
    image_file = Column(String, nullable=False)
    processor = Column(String)
    processing_datetime = Column(TIMESTAMP)

    document = relationship("OriginalDocument", back_populates="processed_images")
    embeddings = relationship("Embedding", back_populates="processed_image")


class RawText(Base):
    __tablename__ = 'raw_texts'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(String, ForeignKey("original_documents.id"))
    raw_text = Column(Text, nullable=False)
    processor = Column(String)
    processing_datetime = Column(TIMESTAMP)

    document = relationship("OriginalDocument", back_populates="raw_texts")
    processed_texts = relationship("ProcessedText", back_populates="raw_text")


class ProcessedText(Base):
    __tablename__ = 'processed_texts'
    
    id = Column(Integer, primary_key=True)
    raw_text_id = Column(Integer, ForeignKey("raw_texts.id"))
    processed_text = Column(Text, nullable=False)
    processor = Column(String)
    processing_datetime = Column(TIMESTAMP)

    raw_text = relationship("RawText", back_populates="processed_texts")
    embeddings = relationship("Embedding", back_populates="processed_text")


class Embedding(Base):
    __tablename__ = 'embeddings'
    
    id = Column(Integer, primary_key=True)
    processed_image_id = Column(Integer, ForeignKey("processed_images.id"))
    processed_text_id = Column(Integer, ForeignKey("processed_texts.id"))
    clip_version = Column(String, nullable=False)
    embeddings = Column(ARRAY(Float, dimensions=1))  # FLOAT8[1024]

    processed_image = relationship("ProcessedImage", back_populates="embeddings")
    processed_text = relationship("ProcessedText", back_populates="embeddings")