from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dsdc import CONFIG, SECRETS

host = "localhost" # TODO: set to docker subnet CONFIG.docker_compose.subnetwork
port = 5432
username = SECRETS.POSTGRES_USER
password = SECRETS.POSTGRES_PASSWORD
db_name = CONFIG.services.postgres.db_name

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()