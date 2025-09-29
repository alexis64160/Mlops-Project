import os
import yaml
import logging
from pathlib import Path
from types import SimpleNamespace
import shlex

def get_project_root(marker=".dsdc_project_root") -> Path:
    """Retrieve DSDC project root"""
    found = False
    
    root_dir = os.environ.get("DSDC_DIR")
    if root_dir is None:
        logging.warning(
            msg=f"DSDC_DIR not defined. Scanning for project root directory..."
        )
    else:
        if not Path(root_dir).exists():
            logging.warning(
                msg=f"DSDC_DIR refers a non valid directory (current_value is {root_dir}). Scanning for project root directory..."
            )
        else:
            files = [p.name for p in Path(root_dir).iterdir()]
            if not marker in files:
                logging.warning(
                    msg=f"DSDC_DIR directory does not contain .dsdc_project_root file, as expected (current_value is {root_dir}). Scanning for project root directory..."
                )
            else:
                project_root = Path(root_dir)
                found = True
                logging.info(
                    msg=f"DSDC_DIR set to {str(project_root)}"
                )
    if not found:
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / marker).exists():
                found = True
                project_root = current
                break
            current = current.parent
    if not found:
        current = Path(os.getcwd()).resolve()
        while current != current.parent:
            if (current / marker).exists():
                found = True
                project_root = current
                break
            current = current.parent
    if not found:
        raise FileNotFoundError(f"Could not find '{marker}' in any parent directory.")
    else:
        return project_root

def load_config_as_namespace(config_path: Path, project_root: Path) -> SimpleNamespace:
    def process_paths(paths_dict):
        processed = {}
        for key, value in paths_dict.items():
            path = Path(value)
            if not path.is_absolute():
                path = project_root / path
            processed[key] = path
        return processed

    def dict_to_namespace(d):
        ns = SimpleNamespace()
        for key, value in d.items():
            if isinstance(value, dict):
                setattr(ns, key, dict_to_namespace(value))
            else:
                setattr(ns, key, value)
        return ns

    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)

    # make all paths absolute
    if config_dict is None:
        return SimpleNamespace()
    elif "paths" in config_dict:
        config_dict["paths"] = process_paths(config_dict["paths"])
    config_dict["paths"]["project_root"] = project_root
    config_dict["paths"]["config"] = config_path
    return dict_to_namespace(config_dict)



def load_env_file(filepath):
    if filepath.exists():
        env_vars = {}
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                val = shlex.split(val)[0] if val else ''
                env_vars[key.strip()] = val.strip()
        return SimpleNamespace(**env_vars)
    else:
        logging.warning(f"no environment file detected")
        return SimpleNamespace()