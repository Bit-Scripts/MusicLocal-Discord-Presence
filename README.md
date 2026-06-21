# 🪟 MusicLocal Discord Presence 🐧

> Pour le français, [rendez-vous ici](README_FR.md).

Show what you're listening to on Discord — with album art stored on your own MinIO/S3 instance. Works with **Windows** (SMTC) and **Linux** (MPRIS), supporting Chrome, Spotify, VLC, WACUP, and more.

![Discord presence example](assets/icon.png)

---

## Features

- Detects the active media session automatically (SMTC on Windows, MPRIS on Linux)
- VLC support via its built-in HTTP API
- Album art uploaded to MinIO/S3 with SHA-256 deduplication cache
- Discord Rich Presence with track title, artist, album art, and progress bar
- System tray icon (Qt on Windows/Linux, GTK on GNOME) with status indicator
- Settings window — no need to edit `.env` by hand
- Single-file executable for Windows and Linux via PyInstaller

---

## Requirements

- Python 3.11+
- A Discord application ([developer portal](https://discord.com/developers/applications))
- A MinIO or S3-compatible instance with a public bucket
- (Optional) VLC with the HTTP interface enabled

---

## Installation

### From release

Download the latest binary from the [Releases](https://github.com/Bit-Scripts/MusicLocal-Discord-Presence/releases) page, place your `.env` file next to it, and run it.

### From source

```bash
git clone https://github.com/Bit-Scripts/MusicLocal-Discord-Presence.git
cd MusicLocal-Discord-Presence

# Windows
pip install -r requirements-windows.txt

# Linux
pip install -r requirements-linux.txt

cp .env-example .env
# Fill in .env or use the settings window after launching
python main.py
```

---

## Configuration

Copy `.env-example` to `.env` and fill in your values, or open the settings window from the system tray after launching.

| Variable | Description | Default |
|---|---|---|
| `DISCORD_CLIENT_ID` | Your Discord application client ID | — |
| `MINIO_URL` | MinIO host (no `https://`) | — |
| `MINIO_ACCESS_KEY` | MinIO access key | — |
| `MINIO_SECRET_KEY` | MinIO secret key | — |
| `MINIO_BUCKET` | Bucket name for album art | `coversimage` |
| `VLC_HOST` | VLC HTTP interface host | `localhost` |
| `VLC_PORT` | VLC HTTP interface port | `8080` |
| `VLC_PASSWORD` | VLC HTTP interface password | — |

---

## VLC setup

1. Open VLC → Tools → Preferences → show **All**
2. Interface → Main interfaces → check **Web**
3. Interface → Main interfaces → Lua → set a **Lua HTTP password**
4. Restart VLC
5. Set `VLC_PASSWORD` in your `.env`

---

## Discord application setup

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create a new application
3. Copy the **Client ID** → set `DISCORD_CLIENT_ID` in `.env`
4. Go to **Rich Presence → Art Assets** and upload player icons (`chrome`, `spotify`, `vlc`, `wacup`, `default_icon`, etc.)

---

## Supported players

| Player | Platform | Via |
|---|---|---|
| Chrome / Edge / Firefox | Windows | SMTC |
| Spotify | Windows | SMTC |
| WACUP | Windows | SMTC |
| VLC | Windows & Linux | HTTP API |
| Spotify / Clementine / Strawberry / mpv | Linux | MPRIS |
| MPD / SMPlayer / MellowPlayer / Lollypop | Linux | MPRIS |

---

## Build from source

```bash
pip install pyinstaller
pyinstaller MusicPresence.spec --distpath dist --workpath build
```

The CI/CD pipeline (GitHub Actions) builds and publishes binaries automatically on each version tag.

---

## License

MIT — see [LICENSE](LICENSE) if present.

---

*Inspired by [MPRIS-Discord-Presence](https://github.com/Bit-Scripts/MPRIS-Discord-Presence)*
