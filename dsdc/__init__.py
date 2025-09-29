from dsdc.utils.config import get_project_root, load_config_as_namespace, load_env_file
PROJECT_ROOT = get_project_root()

CONFIG = load_config_as_namespace(PROJECT_ROOT/"config.yaml", PROJECT_ROOT)
CONFIG.prefix = "DSDC"
CONFIG.paths.secrets = PROJECT_ROOT / ".secrets"

# set up log level
import logging
used_default=False
if hasattr(CONFIG, "settings") and hasattr(CONFIG.settings, "log_level"):
    log_level_str = CONFIG.settings.log_level
else:
    log_level_str = "WARNING"
    used_default = True

log_level = getattr(logging, log_level_str, logging.WARNING)
logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

if used_default:
    logging.warning("⚠️ No log-level set - defaulting to WARNING")