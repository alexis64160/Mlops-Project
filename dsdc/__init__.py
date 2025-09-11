import yaml
from pathlib import Path

from dsdc.utils.config import get_project_root, load_config_as_namespace, load_env_file

PROJECT_ROOT = get_project_root()
CONFIG = load_config_as_namespace(PROJECT_ROOT/"config.yaml", PROJECT_ROOT)
SECRETS = load_env_file(PROJECT_ROOT/".env.secrets")

import os
import logging

log_level_str = CONFIG.logging.level

# Convertir le string en niveau de log numérique
log_level = getattr(logging, log_level_str, logging.WARNING)

logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")