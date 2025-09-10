import psycopg2
import pytest

# Configuration de connexion à la base de données
DB_CONFIG = {
    "dbname": "dsdc_db",       # ← remplace par le nom réel de ta base
    "user": "dsdc_user",
    "password": "toto",
    "host": "localhost",
    "port": 5432
}

# Liste des tables attendues
EXPECTED_TABLES = {
    "original_documents",
    "labels",
    "processed_images",
    "raw_texts",
    "processed_texts",
    "embeddings"
}


@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    yield conn
    conn.close()


def test_tables_exist(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables_in_db = {row[0] for row in cursor.fetchall()}

    missing_tables = EXPECTED_TABLES - tables_in_db

    assert not missing_tables, f"Les tables suivantes sont manquantes : {missing_tables}"