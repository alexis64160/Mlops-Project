import yaml
import os
from pathlib import Path
from dotenv import dotenv_values
from dsdc import CONFIG
import logging

CONFIG_FILE = CONFIG.paths.config
SECRETS_FILE = CONFIG.paths.secrets
OUTPUT_DOT_ENV_FILE = CONFIG.paths.project_root / "services" / ".env"
INTERNAL_PORTS = {
    "auth": 8000,
    "pgadmin": 80,
    "mlflow": 5000,
    "grafana": 3000,
    "prometheus": 9090,
    "redis": 6379,
    "postgres": 5432,
    "flower": 5555,
    "airflow-apiserver": 8080,
    "streamlit": 8501,
    "cadvisor": 8080,
    "extract-text": 8000,
    "process-text": 8000,
    "process-image": 8000,
    "compute-clip-embeddings": 8000,
    "train": 8000,
    "predict": 8000,
    "dsdc-postgres-exporter": 9187,
    "mlflow-postgres-exporter": 9187,
    "airflow-postgres-exporter": 9187,

}


def load_yaml_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_secrets(path):
    if not os.path.exists(path):
        return {}
    return dotenv_values(path)

def generate_env(config, secrets):
    env = {}
    prefix = getattr(CONFIG, "prefix", "")
    if prefix and not prefix.endswith("_"):
        prefix += "_"
    # add config host-exposed ports
    for service, host_port in config.get("host_exposed_ports", {}).items():
        internal_port = INTERNAL_PORTS.get(service) #TODO: UPPER + - -> _
        if not internal_port:
            logging.warning(f"⚠️ Port interne inconnu pour {service}, ignoré.")
            continue
        var_name = f"{prefix}{service.upper().replace('-', '_')}_PORT"
        mapping_var_name = f"{var_name}_MAPPING"
        env[var_name] = str(host_port)
        env[mapping_var_name] = f"{host_port}:{internal_port}"

    # add secrets
    for key, value in secrets.items():
        env[f"{prefix}{key}"] = value

    # additional_values:
    env["AIRFLOW_UID"] = os.getuid()


    return env

def write_env_file(env_dict, path):
    with open(path, "w") as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")

def main():
    logging.info(f"🔧 Génération de {OUTPUT_DOT_ENV_FILE} à partir de {CONFIG_FILE} + {SECRETS_FILE}...")
    if not CONFIG_FILE.exists():
        logging.error(f"❌ Fichier {CONFIG_FILE} introuvable.")
        return
    if not SECRETS_FILE.exists():
        logging.error(f"❌ Fichier {SECRETS_FILE} introuvable.")
        return

    config = load_yaml_config(CONFIG_FILE)
    secrets = load_secrets(SECRETS_FILE)

    env = generate_env(config, secrets)
    write_env_file(env, OUTPUT_DOT_ENV_FILE)

    logging.info(f"✅ Fichier {OUTPUT_DOT_ENV_FILE} généré avec succès.")

if __name__ == "__main__":
    main()