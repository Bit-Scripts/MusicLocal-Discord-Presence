import asyncio
import hashlib
import io
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from PIL import Image
from pypresence import AioPresence
import pypresence

from config import ENV_PATH, CACHE_PATH

load_dotenv(ENV_PATH)

MINIO_URL = os.getenv('MINIO_URL')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
BUCKET_NAME = os.getenv('MINIO_BUCKET', 'coversimage')

ICON_NAMES = {
    # Windows
    'Spotify': 'spotify',
    'Chrome': 'chrome',
    'Microsoft Edge': 'edge',
    'Firefox': 'firefox',
    'VLC media player': 'vlc',
    'foobar2000': 'foobar2000',
    'MusicBee': 'musicbee',
    'wacup.exe': 'wacup',
    # Linux
    'Clementine': 'clementine',
    'Media Player Classic Qute Theater': 'mpc-qt',
    'mpv': 'mpv',
    'Music Player Daemon': 'mpd',
    'SMPlayer': 'smplayer',
    'Lollypop': 'lollypop',
    'Mozilla Firefox': 'firefox',
    'MellowPlayer': 'mellowplayer',
    'Spotube': 'spotube',
    'Strawberry': 'strawberry',
    'default': 'default_icon',
}

if sys.platform == 'win32':
    from backends.smtc import get_track_info
else:
    from backends.mpris import get_track_info

RPC = AioPresence(DISCORD_CLIENT_ID, response_timeout=15)


# ---------- Cache ----------

def _load_cache() -> dict:
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_cache(data: dict):
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


# ---------- MinIO ----------

def _minio_client():
    return Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=True,
    )


def upload_cover(image_bytes: bytes) -> str | None:
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    cache = _load_cache()
    if image_hash in cache:
        print(f"Cache hit: {image_hash[:12]}...")
        return cache[image_hash]

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        img.thumbnail((512, 512), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        size = buf.getbuffer().nbytes
        object_name = f"{image_hash}.png"

        client = _minio_client()
        client.put_object(BUCKET_NAME, object_name, buf, size, content_type='image/png')

        url = f"https://{MINIO_URL}/{BUCKET_NAME}/{object_name}"
        cache[image_hash] = url
        _save_cache(cache)
        print(f"Uploaded: {object_name}")
        return url
    except S3Error as e:
        print(f"MinIO error: {e}")
        return None


# ---------- Discord ----------

def get_icon(source_app: str) -> str:
    return ICON_NAMES.get(source_app, ICON_NAMES['default'])


async def update_discord(title, artist, position_s, duration_s, image_url, source_app):
    now = time.time()
    start_ts = now - position_s
    end_ts = start_ts + duration_s if duration_s > 0 else None

    icon = get_icon(source_app)
    large_image = image_url or icon

    try:
        kwargs = dict(
            details=title,
            state=f"par {artist}",
            start=int(start_ts),
            large_image=large_image,
            small_image=icon,
            large_text="Écoute en cours",
            small_text=source_app or "Lecteur inconnu",
        )
        if end_ts:
            kwargs['end'] = int(end_ts)
        await RPC.update(**kwargs)
    except pypresence.exceptions.ResponseTimeout:
        print("Discord timeout, tentative de reconnexion...")
        try:
            await RPC.connect()
        except Exception:
            pass


async def clear_discord():
    try:
        await RPC.clear()
        print("Présence Discord effacée.")
    except Exception as e:
        print(f"Erreur effacement présence: {e}")


# ---------- Boucle principale ----------

async def main_loop(bridge=None):
    def emit_status(s):
        if bridge:
            try:
                bridge.status_changed.emit(s)
            except Exception:
                pass

    def emit_track(artist, title):
        if bridge:
            try:
                bridge.track_changed.emit(artist, title)
            except Exception:
                pass

    try:
        await RPC.connect()
    except Exception as e:
        print(f"Erreur connexion Discord: {e}")
        emit_status('error')

    print(f"MusicLocal Discord Presence démarré ({sys.platform}).")
    last_log = None
    last_track = None
    last_update_time = 0
    last_position_s = 0
    SYNC_INTERVAL = 15
    SEEK_TOLERANCE = 3

    while True:
        info = await get_track_info()

        if info is None:
            if last_log is not None:
                await clear_discord()
                last_log = None
                last_track = None
                last_update_time = 0
                emit_status('idle')
                emit_track('', '')
            else:
                print("Aucune session multimédia active.")
        else:
            title, artist, image_bytes, source_app, position_s, duration_s = info
            current_track = (title, artist, source_app)
            now = time.time()

            expected_position = last_position_s + (now - last_update_time)
            position_drift = abs(position_s - expected_position)

            track_changed = current_track != last_track
            needs_sync = (now - last_update_time) >= SYNC_INTERVAL
            seeked = last_track is not None and position_drift > SEEK_TOLERANCE

            if track_changed or needs_sync or seeked:
                image_url = upload_cover(image_bytes) if image_bytes else None
                await update_discord(title, artist, position_s, duration_s, image_url, source_app)
                last_update_time = now
                last_position_s = position_s
                last_track = current_track
                emit_status('playing')
                emit_track(artist, title)

                log = f"[{source_app}] {artist} — {title}"
                if log != last_log:
                    print(log)
                    last_log = log

        await asyncio.sleep(5)


# ---------- Entrée ----------

def _get_tray():
    if sys.platform == 'win32':
        from ui.tray_qt import TrayApp
        return TrayApp(main_loop)

    desktop = os.getenv('XDG_CURRENT_DESKTOP', '').lower()
    if 'gnome' in desktop or 'unity' in desktop:
        try:
            from ui.tray_gtk import TrayApp
            return TrayApp(main_loop)
        except Exception:
            pass

    from ui.tray_qt import TrayApp
    return TrayApp(main_loop)


if __name__ == '__main__':
    tray = _get_tray()
    tray.run()
