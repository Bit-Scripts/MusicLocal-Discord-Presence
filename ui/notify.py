import sys


def notify(title: str, message: str, icon_path: str = None, on_click=None):
    """Envoie une notification système native."""
    if sys.platform == 'win32':
        _notify_windows(title, message, icon_path, on_click)
    else:
        _notify_qt(title, message)


def _notify_windows(title: str, message: str, icon_path: str = None, on_click=None):
    try:
        from winotify import Notification, audio
        toast = Notification(
            app_id='MusicLocal Discord Presence',
            title=title,
            msg=message,
            icon=icon_path or '',
        )
        toast.set_audio(audio.Default, loop=False)
        if on_click:
            toast.add_actions(label='Ouvrir', launch=on_click)
        toast.show()
    except Exception as e:
        print(f"Notification échouée: {e}")
        _notify_qt(title, message)


def _notify_qt(title: str, message: str):
    try:
        from PyQt6.QtWidgets import QSystemTrayIcon, QApplication
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if hasattr(widget, '_tray'):
                    widget._tray.showMessage(title, message,
                        QSystemTrayIcon.MessageIcon.Information, 6000)
                    return
    except Exception:
        pass
