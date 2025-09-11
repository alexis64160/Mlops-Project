CREATE TABLE IF NOT EXISTS original_documents(
    id TEXT PRIMARY KEY,
    original_file TEXT NOT NULL,
    import_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS labels(
    id SERIAL PRIMARY KEY,
    document_id TEXT REFERENCES original_documents(id),
    source TEXT,
    label INT NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_images(
    id SERIAL PRIMARY KEY,
    document_id TEXT REFERENCES original_documents(id),
    image_file TEXT NOT NULL,
    processor TEXT,
    processing_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_texts(
    id SERIAL PRIMARY KEY,
    document_id TEXT REFERENCES original_documents(id),
    raw_text TEXT NOT NULL,
    processor TEXT,
    processing_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_texts(
    id SERIAL PRIMARY KEY,
    raw_text_id INTEGER REFERENCES raw_texts(id),
    processed_text TEXT NOT NULL,
    processor TEXT,
    processing_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embeddings(
    id SERIAL PRIMARY KEY,
    processed_image_id INTEGER REFERENCES processed_images(id),
    processed_text_id INTEGER REFERENCES processed_texts(id),
    clip_version TEXT NOT NULL,
    embeddings FLOAT8[1024]
);

CREATE INDEX idx_labels_document_id ON labels(document_id);
CREATE INDEX idx_processed_images_document_id ON processed_images(document_id);
CREATE INDEX idx_raw_texts_document_id ON raw_texts(document_id);
CREATE INDEX idx_processed_texts_raw_text_id ON processed_texts(raw_text_id);
CREATE INDEX idx_embeddings_text_id ON embeddings(processed_text_id);
CREATE INDEX idx_embeddings_image_id ON embeddings(processed_image_id);
