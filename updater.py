import sys
import requests
from packaging.version import Version
from version import __version__, GITHUB_REPO

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def _asset_name() -> str:
    if sys.platform == 'win32':
        return 'MusicPresence-Setup-latest.exe'
    return 'MusicPresence-latest-x86_64.AppImage'


def check_for_update() -> tuple[str, str] | None:
    """Retourne (latest_version, download_url) si une mise à jour est disponible, sinon None."""
    try:
        r = requests.get(API_URL, timeout=10, headers={'Accept': 'application/vnd.github+json'})
        if r.status_code != 200:
            return None
        data = r.json()
        latest = data.get('tag_name', '').lstrip('v')
        if not latest:
            return None
        if Version(latest) <= Version(__version__):
            return None

        # Cherche le setup Windows ou l'AppImage Linux
        assets = data.get('assets', [])
        for asset in assets:
            name = asset['name']
            if sys.platform == 'win32' and name.startswith('MusicPresence-Setup-') and name.endswith('.exe'):
                return latest, asset['browser_download_url']
            if sys.platform != 'win32' and name.endswith('.AppImage'):
                return latest, asset['browser_download_url']
    except Exception as e:
        print(f"Vérification mise à jour échouée: {e}")
    return None
