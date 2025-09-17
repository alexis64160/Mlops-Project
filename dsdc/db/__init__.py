from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dsdc import CONFIG, SECRETS
import logging

DSDCBase = declarative_base()

username = SECRETS.DSDC_USER
password = SECRETS.DSDC_PASSWORD
db_name = CONFIG.services.postgres.dsdc_db_name

if getattr(CONFIG.settings, "locally_run", False):
    prefix = "postgresql"
    host = "localhost" 
    port = 5432
    address = f"{host}:{port}"
else:
    prefix = "postgresql+psycopg2"
    address = "dsdc-postgres" # TODO: set to docker subnet CONFIG.docker_compose.subnetwork

DATABASE_URL = f"{prefix}://{username}:{password}@{address}/{db_name}"
logging.info(f"Generation SQLAlchemy engine with url {DATABASE_URL}") # TODO remove password from logs    
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)