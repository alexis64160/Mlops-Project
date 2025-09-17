from dsdc.utils.config import get_project_root, load_config_as_namespace, load_env_file
PROJECT_ROOT = get_project_root()
secrets_file = PROJECT_ROOT/".env.secrets"
SECRETS = load_env_file(PROJECT_ROOT/".env.secrets")
CONFIG = load_config_as_namespace(PROJECT_ROOT/"config.yaml", PROJECT_ROOT)


import yaml
import logging

if hasattr(CONFIG, "logging") and hasattr(CONFIG.logging, "level"):
    log_level_str = CONFIG.logging.level
else:
    log_level_str = "warning"
log_level = getattr(logging, log_level_str, logging.WARNING)
logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")