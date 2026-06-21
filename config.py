import os
import sys
from pathlib import Path


def get_config_dir() -> Path:
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home()))
    else:
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    config_dir = base / 'MusicPresence'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


CONFIG_DIR = get_config_dir()
ENV_PATH   = CONFIG_DIR / '.env'
CACHE_PATH = CONFIG_DIR / 'image_cache.json'
