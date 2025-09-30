import psycopg2
import pytest
import os
from dsdc import CONFIG
from dotenv import load_dotenv

load_dotenv(CONFIG.paths.project_root/"services"/".env")

# Configuration de connexion à la base de données
DB_CONFIG = {
    "dbname": os.environ["DSDC_POSTGRES_DSDC_DB"],
    "user": os.environ["DSDC_POSTGRES_DSDC_USER"],
    "password": os.environ["DSDC_POSTGRES_DSDC_PASSWORD"],
    "host": "localhost",
    "port": os.environ["DSDC_POSTGRES_PORT"]
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


def test_db_connection(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result == (1,), "Connexion à la base échouée ou requête simple non fonctionnelle"


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