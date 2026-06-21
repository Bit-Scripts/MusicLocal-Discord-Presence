import os
import requests
import winsdk.windows.media.control as wmc
import winsdk.windows.storage.streams as wss

VLC_HOST = os.getenv('VLC_HOST', 'localhost')
VLC_PORT = int(os.getenv('VLC_PORT', '8080'))
VLC_PASSWORD = os.getenv('VLC_PASSWORD', '')


# ---------- VLC ----------

def get_vlc_track_info():
    """Interroge l'API HTTP de VLC. Retourne un tuple ou None."""
    try:
        r = requests.get(
            f"http://{VLC_HOST}:{VLC_PORT}/requests/status.json",
            auth=('', VLC_PASSWORD),
            timeout=1,
        )
        if r.status_code != 200:
            return None
        data = r.json()

        if data.get('state') != 'playing':
            return None

        category = data.get('information', {}).get('category', {})
        meta = category.get('meta', {})

        title = meta.get('title') or meta.get('filename', 'Titre inconnu')
        artist = meta.get('artist', 'Artiste inconnu')
        position_s = float(data.get('time', 0))
        duration_s = float(data.get('length', 0))

        image_bytes = None
        try:
            art_r = requests.get(
                f"http://{VLC_HOST}:{VLC_PORT}/art",
                auth=('', VLC_PASSWORD),
                timeout=3,
            )
            if art_r.status_code == 200 and 'image' in art_r.headers.get('Content-Type', ''):
                image_bytes = art_r.content
        except Exception:
            pass

        return title, artist, image_bytes, 'VLC media player', position_s, duration_s
    except Exception:
        return None


# ---------- SMTC ----------

async def _get_thumbnail_bytes(session) -> bytes | None:
    try:
        props = await session.try_get_media_properties_async()
        thumb_ref = props.thumbnail
        if thumb_ref is None:
            return None
        stream = await thumb_ref.open_read_async()
        size = stream.size
        reader = wss.DataReader(stream)
        await reader.load_async(size)
        buf = bytearray(size)
        reader.read_bytes(buf)
        return bytes(buf)
    except Exception as e:
        print(f"Erreur lecture miniature: {e}")
        return None


async def get_track_info():
    """VLC en priorité, puis SMTC. Retourne un tuple ou None."""
    vlc = get_vlc_track_info()
    if vlc:
        return vlc

    try:
        manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()
        if session is None:
            return None

        props = await session.try_get_media_properties_async()
        title = props.title or "Titre inconnu"
        artist = props.artist or "Artiste inconnu"
        source_app = session.source_app_user_model_id or ""

        tl = session.get_timeline_properties()
        position_s = tl.position.total_seconds() if tl else 0
        duration_s = tl.end_time.total_seconds() if tl else 0

        image_bytes = await _get_thumbnail_bytes(session)
        return title, artist, image_bytes, source_app, position_s, duration_s
    except Exception as e:
        print(f"Erreur SMTC: {e}")
        return None
