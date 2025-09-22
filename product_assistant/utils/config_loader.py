import yaml
import os
from pathlib import Path
from product_assistant.logger import GLOBAL_LOGGER as log

def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def load_config(config_path: str | None=None) -> dict:
    """
    Resolve config path  relatibly irrespective of CMD
    Priority: explicit arg > CONFIG_PATH env > <project_root>/config/config.yaml
    """
    env_path = os.getenv("CONFIG_PATH")
    if config_path is None:
        config_path = env_path or str(_project_root() / "config" / "config.yaml")
    
    path = Path(config_path)
    if not path.is_absolute():
        path = _project_root / path
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}