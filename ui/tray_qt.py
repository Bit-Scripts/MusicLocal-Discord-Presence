import os
import sys
import threading
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import QObject, pyqtSignal, Qt

from ui.settings import SettingsWindow

BASE_DIR  = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICONS_DIR = BASE_DIR / 'playersIcons'
ASSETS_DIR = BASE_DIR / 'assets'


def _make_status_icon(color: str, fg_pixmap: QPixmap = None) -> QIcon:
    size = 64
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    from PyQt6.QtGui import QPainter, QBrush
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(color)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, size, size)
    if fg_pixmap:
        p.drawPixmap(0, 0, size, size, fg_pixmap)
    p.end()
    return QIcon(px)


class _Bridge(QObject):
    status_changed = pyqtSignal(str)   # 'playing', 'idle', 'error'
    track_changed  = pyqtSignal(str, str)  # artist, title


class TrayApp:
    def __init__(self, loop_fn):
        """
        loop_fn : coroutine async def main_loop(bridge) à exécuter dans un thread.
        """
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._bridge = _Bridge()
        self._loop_fn = loop_fn
        self._current_track = ('', '')

        # Chargement du foreground (notes + badges, fond transparent)
        fg_path = ASSETS_DIR / 'icon_fg.png'
        fg_px = QPixmap(str(fg_path)) if fg_path.exists() else None

        app_icon_path = ASSETS_DIR / 'icon.png'
        if app_icon_path.exists():
            self._app.setWindowIcon(QIcon(str(app_icon_path)))

        self._icon_default = _make_status_icon('#5865F2', fg_px)  # violet Discord
        self._icon_playing = _make_status_icon('#57F287', fg_px)  # vert
        self._icon_idle    = _make_status_icon('#FEE75C', fg_px)  # jaune
        self._icon_error   = _make_status_icon('#ED4245', fg_px)  # rouge

        self._tray = QSystemTrayIcon(self._icon_default)
        self._tray.setToolTip('MusicLocal Discord Presence')

        menu = QMenu()
        self._status_action = menu.addAction('En attente...')
        self._status_action.setEnabled(False)
        menu.addSeparator()
        menu.addAction('Paramètres', self._open_settings)
        menu.addSeparator()
        menu.addAction('Quitter', self._quit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_click)

        self._bridge.status_changed.connect(self._on_status)
        self._bridge.track_changed.connect(self._on_track)

    def _on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._open_settings()

    def _on_status(self, status: str):
        icons = {
            'playing': self._icon_playing,
            'idle':    self._icon_idle,
            'error':   self._icon_error,
        }
        self._tray.setIcon(icons.get(status, self._icon_default))

    def _on_track(self, artist: str, title: str):
        self._current_track = (artist, title)
        label = f'♪ {artist} — {title}' if title else 'En attente...'
        self._status_action.setText(label[:60])
        self._tray.setToolTip(f'MusicLocal\n{label}')

    def _open_settings(self):
        win = SettingsWindow()
        win.exec()

    def _quit(self):
        self._tray.hide()
        self._app.quit()

    def run(self):
        self._app.setQuitOnLastWindowClosed(False)
        self._tray.show()

        def _thread():
            import asyncio
            asyncio.run(self._loop_fn(self._bridge))

        t = threading.Thread(target=_thread, daemon=True)
        t.start()

        sys.exit(self._app.exec())
