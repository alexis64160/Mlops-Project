CREATE TABLE IF NOT EXISTS original_documents(
    id TEXT PRIMARY KEY,
    original_file TEXT NOT NULL,
    import_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_image_file TEXT,
    raw_ocr TEXT,
    processed_ocr TEXT
);

CREATE TABLE IF NOT EXISTS labels(
    id SERIAL PRIMARY KEY,
    document_id TEXT,
    source TEXT,
    label INT
);

CREATE TABLE IF NOT EXISTS processed_images(
    id SERIAL PRIMARY KEY,
    document_id TEXT,
    image_file TEXT,
    processor TEXT,
    processing_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_texts(
    id SERIAL PRIMARY KEY,
    document_id TEXT,
    processor TEXT,
    processing_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_texts(
    id SERIAL PRIMARY KEY,
    raw_text SERIAL,
    processor TEXT,
    processing_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embeddings(
    id SERIAL PRIMARY KEY,
    processed_image SERIAL NOT NULL,
    processed_text SERIAL NOT NULL,
    clip_version TEXT NOT NULL,
    embeddings FLOAT8[1024]
);

