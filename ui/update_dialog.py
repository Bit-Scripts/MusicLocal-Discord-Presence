import os
import sys
import threading
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont
import requests


def get_downloads_dir() -> Path:
    if sys.platform == 'win32':
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            path, _ = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')
            return Path(path)
        except Exception:
            pass
    return Path.home() / 'Downloads'


class _DownloadSignals(QObject):
    progress = pyqtSignal(int)
    done     = pyqtSignal(str)   # chemin du fichier téléchargé
    error    = pyqtSignal(str)


class UpdateDialog(QDialog):
    def __init__(self, version: str, download_url: str, parent=None):
        super().__init__(parent)
        self._version = version
        self._download_url = download_url
        self._signals = _DownloadSignals()
        self._dest_path = None

        self.setWindowTitle('Mise à jour disponible')
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel(f'MusicLocal Discord Presence v{version}')
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        layout.addWidget(QLabel('Une nouvelle version est disponible.\nVoulez-vous la télécharger et l\'installer ?'))

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status = QLabel('')
        self._status.setVisible(False)
        layout.addWidget(self._status)

        btn_layout = QHBoxLayout()
        self._btn_update = QPushButton('Mettre à jour')
        self._btn_update.setDefault(True)
        self._btn_cancel = QPushButton('Plus tard')
        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_cancel)
        btn_layout.addWidget(self._btn_update)
        layout.addLayout(btn_layout)

        self._btn_update.clicked.connect(self._start_download)
        self._btn_cancel.clicked.connect(self.reject)

        self._signals.progress.connect(self._on_progress)
        self._signals.done.connect(self._on_done)
        self._signals.error.connect(self._on_error)

    def _start_download(self):
        self._btn_update.setEnabled(False)
        self._btn_cancel.setEnabled(False)
        self._progress.setVisible(True)
        self._status.setVisible(True)
        self._status.setText('Téléchargement en cours...')

        filename = self._download_url.split('/')[-1]
        dest = get_downloads_dir() / filename
        self._dest_path = str(dest)

        def _download():
            try:
                r = requests.get(self._download_url, stream=True, timeout=120)
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            self._signals.progress.emit(int(downloaded / total * 100))
                self._signals.done.emit(str(dest))
            except Exception as e:
                self._signals.error.emit(str(e))

        threading.Thread(target=_download, daemon=True).start()

    def _on_progress(self, value: int):
        self._progress.setValue(value)

    def _on_done(self, path: str):
        self._status.setText(f'Téléchargé dans {get_downloads_dir().name}/\nLancement de l\'installation...')
        self._progress.setValue(100)

        if sys.platform == 'win32':
            os.startfile(path)
        else:
            os.chmod(path, 0o755)
            import subprocess
            subprocess.Popen([path])

        # Ferme l'app après lancement du setup
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()

    def _on_error(self, msg: str):
        self._status.setText(f'Erreur : {msg}')
        self._btn_cancel.setEnabled(True)
        self._btn_cancel.setText('Fermer')
