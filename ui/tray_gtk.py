import os
import sys
import threading
from pathlib import Path

try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import Gtk, AppIndicator3, GLib
    HAS_GTK = True
except Exception:
    HAS_GTK = False

ICONS_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'playersIcons'


class TrayApp:
    def __init__(self, loop_fn):
        if not HAS_GTK:
            raise RuntimeError("GTK/AppIndicator3 non disponible.")

        self._loop_fn = loop_fn
        self._status_item = None

        icon_path = str(ICONS_DIR / 'default_icon.png')
        self._indicator = AppIndicator3.Indicator.new(
            'musicpresence',
            icon_path,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self._indicator.set_menu(self._build_menu())

    def _build_menu(self):
        menu = Gtk.Menu()

        self._status_item = Gtk.MenuItem(label='En attente...')
        self._status_item.set_sensitive(False)
        menu.append(self._status_item)

        menu.append(Gtk.SeparatorMenuItem())

        settings_item = Gtk.MenuItem(label='Paramètres')
        settings_item.connect('activate', self._open_settings)
        menu.append(settings_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label='Quitter')
        quit_item.connect('activate', lambda _: Gtk.main_quit())
        menu.append(quit_item)

        menu.show_all()
        return menu

    def update_track(self, artist: str, title: str):
        label = f'♪ {artist} — {title}' if title else 'En attente...'
        GLib.idle_add(self._status_item.set_label, label[:60])

    def update_status(self, status: str):
        pass  # AppIndicator3 ne supporte pas facilement le changement de couleur d'icône

    def _open_settings(self, _=None):
        # Ouvre la fenêtre Qt settings dans un sous-processus ou thread
        from PyQt6.QtWidgets import QApplication
        from ui.settings import SettingsWindow
        app = QApplication.instance() or QApplication(sys.argv)
        win = SettingsWindow()
        win.exec()

    def run(self):
        def _thread():
            import asyncio

            class _Bridge:
                def __init__(self, tray):
                    self._tray = tray

                def status_changed_emit(self, status):
                    self._tray.update_status(status)

                def track_changed_emit(self, artist, title):
                    self._tray.update_track(artist, title)

            asyncio.run(self._loop_fn(_Bridge(self)))

        t = threading.Thread(target=_thread, daemon=True)
        t.start()
        Gtk.main()
