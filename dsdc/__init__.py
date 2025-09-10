import yaml
from pathlib import Path

from dsdc.utils import get_project_root, load_config_as_namespace, load_env_file

PROJECT_ROOT = get_project_root()
CONFIG = load_config_as_namespace(PROJECT_ROOT/"config.yaml", PROJECT_ROOT)
SECRETS = load_env_file(PROJECT_ROOT/".env.secrets")

