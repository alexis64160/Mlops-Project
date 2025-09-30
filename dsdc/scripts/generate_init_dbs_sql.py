from dsdc import CONFIG
from dotenv import dotenv_values
import logging

# Config
ENV_SECRETS_FILE = CONFIG.paths.secrets
OUTPUT_SQL_FILE = CONFIG.paths.project_root / "services" / "postgres" / "init_dbs" / "init_dbs_and_users.sql"

# Chargement des secrets
secrets = dotenv_values(ENV_SECRETS_FILE)

# Préparation des sections par utilisateur/db
db_users = {
    "dsdc": {
        "user": secrets["POSTGRES_DSDC_USER"],
        "password": secrets["POSTGRES_DSDC_PASSWORD"],
        "db": secrets["POSTGRES_DSDC_DB"]
    },
    "airflow": {
        "user": secrets["POSTGRES_AIRFLOW_USER"],
        "password": secrets["POSTGRES_AIRFLOW_PASSWORD"],
        "db": secrets["POSTGRES_AIRFLOW_DB"]
    },
    "mlflow": {
        "user": secrets["POSTGRES_MLFLOW_USER"],
        "password": secrets["POSTGRES_MLFLOW_PASSWORD"],
        "db": secrets["POSTGRES_MLFLOW_DB"]
    }
}

exporter_user = secrets["POSTGRES_EXPORTER_USER"]

sql_lines = []

# Création des utilisateurs et bases de données
for name, info in db_users.items():
    sql_lines.append(f"CREATE USER {info['user']} WITH PASSWORD '{info['password']}';")
    sql_lines.append(f"CREATE DATABASE {info['db']} OWNER {info['user']};")
    sql_lines.append("")  # Ligne vide pour la lisibilité

# Création de l'utilisateur exporter
sql_lines.append(f"CREATE USER {exporter_user} WITH PASSWORD '{secrets['POSTGRES_EXPORTER_PASSWORD']}';")
sql_lines.append("")

# Droits en lecture seule pour exporter_user
for name, info in db_users.items():
    db = info["db"]
    sql_lines.append(f"-- Read-only permissions for {exporter_user} on {db}")
    sql_lines.append(f"GRANT CONNECT ON DATABASE {db} TO {exporter_user};")
    sql_lines.append(f"""\\c {db}
GRANT USAGE ON SCHEMA public TO {exporter_user};
GRANT SELECT ON ALL TABLES IN SCHEMA public TO {exporter_user};
ALTER DEFAULT PRIVILEGES FOR ROLE {info['user']} IN SCHEMA public GRANT SELECT ON TABLES TO {exporter_user};
""")

# Écriture du fichier SQL
with open(OUTPUT_SQL_FILE, "w") as f:
    f.write("\n".join(sql_lines))

logging.info(f"✅ Fichier SQL généré : {OUTPUT_SQL_FILE}")
