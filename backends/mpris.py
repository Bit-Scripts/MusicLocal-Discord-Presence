import requests

try:
    import dbus
    import pympris
except ImportError:
    dbus = None
    pympris = None


def _get_session_bus():
    return dbus.SessionBus()


def _get_active_player():
    if dbus is None:
        return None, None
    session_bus = _get_session_bus()
    services = [s for s in session_bus.list_names() if s.startswith('org.mpris.MediaPlayer2.')]
    if not services:
        return None, None

    players_ids = list(pympris.available_players())
    if not players_ids:
        return None, None

    bus = dbus.SessionBus()
    mp = pympris.MediaPlayer(players_ids[0], bus)
    player_name = mp.root.Identity
    player_bus = session_bus.get_object(services[0], '/org/mpris/MediaPlayer2')
    props = dbus.Interface(player_bus, 'org.freedesktop.DBus.Properties')
    return props, player_name


def _get_position_duration(player_name_service):
    if dbus is None:
        return 0, 0
    session_bus = _get_session_bus()
    for service in session_bus.list_names():
        if service.startswith('org.mpris.MediaPlayer2.'):
            try:
                player = session_bus.get_object(service, '/org/mpris/MediaPlayer2')
                props = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
                metadata = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                position = props.Get('org.mpris.MediaPlayer2.Player', 'Position')
                duration = metadata.get('mpris:length', 0)
                return int(position) / 1_000_000, int(duration) / 1_000_000
            except dbus.DBusException:
                continue
    return 0, 0


async def get_track_info():
    """Retourne un tuple (title, artist, image_bytes, source_app, position_s, duration_s) ou None."""
    if dbus is None:
        return None

    props, player_name = _get_active_player()
    if props is None:
        return None

    try:
        metadata = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        title = str(metadata.get('xesam:title', 'Titre inconnu'))
        artist = str(metadata.get('xesam:artist', ['Artiste inconnu'])[0])
        art_url = str(metadata.get('mpris:artUrl', ''))

        position_s, duration_s = _get_position_duration(player_name)

        image_bytes = None
        if art_url:
            try:
                if art_url.startswith('file://'):
                    with open(art_url[7:], 'rb') as f:
                        image_bytes = f.read()
                else:
                    r = requests.get(art_url, timeout=5)
                    if r.status_code == 200:
                        image_bytes = r.content
            except Exception:
                pass

        return title, artist, image_bytes, player_name, position_s, duration_s
    except Exception as e:
        print(f"Erreur MPRIS: {e}")
        return None
