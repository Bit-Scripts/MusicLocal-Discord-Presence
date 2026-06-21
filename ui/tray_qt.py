import os
import sys
import threading
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import QObject, pyqtSignal, Qt

from ui.settings import SettingsWindow
from ui.notify import notify
from version import __version__

BASE_DIR   = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICONS_DIR  = BASE_DIR / 'playersIcons'
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
    status_changed = pyqtSignal(str)
    track_changed  = pyqtSignal(str, str)
    update_available = pyqtSignal(str, str)  # version, download_url


class TrayApp:
    def __init__(self, loop_fn):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._bridge = _Bridge()
        self._loop_fn = loop_fn
        self._settings_win = None
        self._update_action = None
        self._pending_update = None  # (version, url)

        fg_path = ASSETS_DIR / 'icon_fg.png'
        fg_px = QPixmap(str(fg_path)) if fg_path.exists() else None

        app_icon_path = ASSETS_DIR / 'icon.png'
        if app_icon_path.exists():
            self._app.setWindowIcon(QIcon(str(app_icon_path)))

        self._icon_default = _make_status_icon('#5865F2', fg_px)
        self._icon_playing = _make_status_icon('#57F287', fg_px)
        self._icon_idle    = _make_status_icon('#FEE75C', fg_px)
        self._icon_error   = _make_status_icon('#ED4245', fg_px)
        self._icon_update  = _make_status_icon('#EB459E', fg_px)  # rose = update dispo

        self._tray = QSystemTrayIcon(self._icon_default)
        self._tray.setToolTip(f'MusicLocal Discord Presence v{__version__}')

        self._menu = QMenu()
        self._status_action = self._menu.addAction('En attente...')
        self._status_action.setEnabled(False)
        self._menu.addSeparator()
        self._menu.addAction('Paramètres', self._open_settings)
        self._menu.addSeparator()
        self._menu.addAction('Quitter', self._quit)

        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_tray_click)
        self._tray.messageClicked.connect(self._on_notification_click)

        self._bridge.status_changed.connect(self._on_status)
        self._bridge.track_changed.connect(self._on_track)
        self._bridge.update_available.connect(self._on_update_available)

    def _on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._open_settings()

    def _on_status(self, status: str):
        if self._pending_update:
            return  # garde l'icône rose tant qu'une update est dispo
        icons = {
            'playing': self._icon_playing,
            'idle':    self._icon_idle,
            'error':   self._icon_error,
        }
        self._tray.setIcon(icons.get(status, self._icon_default))

    def _on_track(self, artist: str, title: str):
        label = f'♪ {artist} — {title}' if title else 'En attente...'
        self._status_action.setText(label[:60])
        self._tray.setToolTip(f'MusicLocal v{__version__}\n{label}')

    def _on_update_available(self, version: str, url: str):
        self._pending_update = (version, url)
        self._tray.setIcon(self._icon_update)

        # Entrée dans le menu
        if self._update_action is None:
            update_item = self._menu.insertSection(
                self._menu.actions()[2], f'Mise à jour v{version} disponible'
            )
            install_item = self._menu.addAction(f'Installer v{version}')
            install_item.triggered.connect(self._open_update_dialog)
            self._menu.insertAction(self._menu.actions()[2], install_item)
            self._update_action = install_item

        # Qt balloon tip : messageClicked ouvre le dialog directement
        self._tray.showMessage(
            'Mise à jour disponible',
            f'MusicLocal v{version} est disponible — cliquez pour installer.',
            QSystemTrayIcon.MessageIcon.Information,
            8000,
        )

    def _on_notification_click(self):
        if self._pending_update:
            self._open_update_dialog()

    def _open_update_dialog(self):
        if not self._pending_update:
            return
        from ui.update_dialog import UpdateDialog
        version, url = self._pending_update
        dlg = UpdateDialog(version, url)
        dlg.exec()

    def _open_settings(self):
        if self._settings_win is None:
            self._settings_win = SettingsWindow()
        self._settings_win.show()
        self._settings_win.raise_()
        self._settings_win.activateWindow()

    def _quit(self):
        self._tray.hide()
        self._app.quit()

    def run(self):
        self._app.setQuitOnLastWindowClosed(False)
        self._tray.show()

        def _loop_thread():
            import asyncio
            asyncio.run(self._loop_fn(self._bridge))

        def _update_thread():
            from updater import check_for_update
            result = check_for_update()
            if result:
                version, url = result
                self._bridge.update_available.emit(version, url)

        threading.Thread(target=_loop_thread, daemon=True).start()
        threading.Thread(target=_update_thread, daemon=True).start()

        sys.exit(self._app.exec())
