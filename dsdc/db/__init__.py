from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dsdc import CONFIG
import logging
import os

DSDCBase = declarative_base()

username = os.environ["DSDC_POSTGRES_DSDC_USER"]
password = os.environ["DSDC_POSTGRES_DSDC_PASSWORD"]
db_name = os.environ["DSDC_POSTGRES_DSDC_DB"]

if getattr(CONFIG.settings, "locally_run", False):
    prefix = "postgresql"
    host = "localhost" 
    port = 5432
    address = f"{host}:{port}"
else:
    prefix = "postgresql+psycopg2"
    host = "localhost" 
    port = 5432
    address = "dsdc-postgres" # TODO: set to docker subnet CONFIG.docker_compose.subnetwork

DATABASE_URL = f"{prefix}://{username}:{password}@{address}/{db_name}"
logging.info(f"Generation SQLAlchemy engine with url {DATABASE_URL}") # TODO remove password from logs    
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)