import os
import sys
import tempfile
import threading
import requests
from packaging.version import Version
from version import __version__, GITHUB_REPO

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def _asset_name() -> str:
    if sys.platform == 'win32':
        return 'MusicPresence.exe'
    return 'MusicPresence'


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

        asset_name = _asset_name()
        for asset in data.get('assets', []):
            if asset['name'] == asset_name:
                return latest, asset['browser_download_url']
    except Exception as e:
        print(f"Vérification mise à jour échouée: {e}")
    return None


def download_and_install(download_url: str, new_version: str = '', on_progress=None, on_done=None, on_error=None):
    """Télécharge et installe la mise à jour dans un thread séparé."""
    def _run():
        try:
            r = requests.get(download_url, stream=True, timeout=60)
            total = int(r.headers.get('content-length', 0))
            downloaded = 0

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
            for chunk in r.iter_content(chunk_size=65536):
                tmp.write(chunk)
                downloaded += len(chunk)
                if on_progress and total:
                    on_progress(int(downloaded / total * 100))
            tmp.close()

            _replace_and_restart(tmp.name, new_version)
            if on_done:
                on_done()
        except Exception as e:
            print(f"Erreur mise à jour: {e}")
            if on_error:
                on_error(str(e))

    threading.Thread(target=_run, daemon=True).start()


def _replace_and_restart(new_exe_path: str, new_version: str):
    from version import __version__ as old_version
    current = sys.executable if getattr(sys, 'frozen', False) else None

    if sys.platform == 'win32' and current:
        bat = tempfile.NamedTemporaryFile(delete=False, suffix='.bat', mode='w')
        bat.write('@echo off\n')
        bat.write('timeout /t 2 /nobreak >nul\n')
        bat.write(f'move /y "{new_exe_path}" "{current}"\n')
        bat.write(f'start "" "{current}" --updated-from {old_version}\n')
        bat.write('del "%~f0"\n')
        bat.close()
        os.startfile(bat.name)
        sys.exit(0)

    elif sys.platform != 'win32' and current:
        os.chmod(new_exe_path, 0o755)
        os.replace(new_exe_path, current)
        os.execv(current, sys.argv + [f'--updated-from={old_version}'])

    else:
        print(f"Mode dev — nouveau binaire téléchargé dans : {new_exe_path}")
