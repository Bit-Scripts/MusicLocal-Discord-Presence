# 🪟 MusicLocal Discord Presence 🐧

> For English, [go here](README.md).

Affichez ce que vous écoutez sur Discord — avec les pochettes stockées sur votre propre instance MinIO/S3. Fonctionne sur **Windows** (SMTC) et **Linux** (MPRIS), avec Chrome, Spotify, VLC, WACUP, et plus encore.

---

## Fonctionnalités

- Détection automatique de la session multimédia active (SMTC sous Windows, MPRIS sous Linux)
- Support VLC via son interface HTTP intégrée
- Pochettes uploadées sur MinIO/S3 avec cache par déduplication SHA-256
- Discord Rich Presence avec titre, artiste, pochette et barre de progression
- Icône en zone de notification (Qt sous Windows/Linux, GTK sous GNOME) avec indicateur de statut
- Fenêtre de paramètres — pas besoin d'éditer `.env` à la main
- Exécutable en fichier unique pour Windows et Linux via PyInstaller

---

## Prérequis

- Python 3.11+
- Une application Discord ([portail développeur](https://discord.com/developers/applications))
- Une instance MinIO ou compatible S3 avec un bucket public
- (Optionnel) VLC avec l'interface HTTP activée

---

## Installation

### Depuis une release

Téléchargez le dernier binaire depuis la page [Releases](https://github.com/Bit-Scripts/MusicLocal-Discord-Presence/releases), placez votre fichier `.env` à côté et lancez-le.

### Depuis les sources

```bash
git clone https://github.com/Bit-Scripts/MusicLocal-Discord-Presence.git
cd MusicLocal-Discord-Presence

# Windows
pip install -r requirements-windows.txt

# Linux
pip install -r requirements-linux.txt

cp .env-example .env
# Remplissez .env ou utilisez la fenêtre de paramètres après le lancement
python main.py
```

---

## Configuration

Copiez `.env-example` vers `.env` et renseignez vos valeurs, ou ouvrez la fenêtre de paramètres depuis la zone de notification après le lancement.

| Variable | Description | Défaut |
|---|---|---|
| `DISCORD_CLIENT_ID` | Client ID de votre application Discord | — |
| `MINIO_URL` | Hôte MinIO (sans `https://`) | — |
| `MINIO_ACCESS_KEY` | Clé d'accès MinIO | — |
| `MINIO_SECRET_KEY` | Clé secrète MinIO | — |
| `MINIO_BUCKET` | Nom du bucket pour les pochettes | `coversimage` |
| `VLC_HOST` | Hôte de l'interface HTTP VLC | `localhost` |
| `VLC_PORT` | Port de l'interface HTTP VLC | `8080` |
| `VLC_PASSWORD` | Mot de passe de l'interface HTTP VLC | — |

---

## Configuration de VLC

1. Ouvrir VLC → Outils → Préférences → afficher **Tout**
2. Interface → Interfaces principales → cocher **Web**
3. Interface → Interfaces principales → Lua → définir un **mot de passe Lua HTTP**
4. Redémarrer VLC
5. Renseigner `VLC_PASSWORD` dans votre `.env`

---

## Configuration de l'application Discord

1. Aller sur [discord.com/developers/applications](https://discord.com/developers/applications)
2. Créer une nouvelle application
3. Copier le **Client ID** → renseigner `DISCORD_CLIENT_ID` dans `.env`
4. Aller dans **Rich Presence → Art Assets** et uploader les icônes des lecteurs (`chrome`, `spotify`, `vlc`, `wacup`, `default_icon`, etc.)

---

## Lecteurs supportés

| Lecteur | Plateforme | Via |
|---|---|---|
| Chrome / Edge / Firefox | Windows | SMTC |
| Spotify | Windows | SMTC |
| WACUP | Windows | SMTC |
| VLC | Windows & Linux | API HTTP |
| Spotify / Clementine / Strawberry / mpv | Linux | MPRIS |
| MPD / SMPlayer / MellowPlayer / Lollypop | Linux | MPRIS |

---

## Compilation depuis les sources

```bash
pip install pyinstaller
pyinstaller MusicPresence.spec --distpath dist --workpath build
```

Le pipeline CI/CD (GitHub Actions) compile et publie les binaires automatiquement à chaque tag de version.

---

## Licence

MIT — voir [LICENSE](LICENSE) si présent.

---

*Inspiré par [MPRIS-Discord-Presence](https://github.com/Bit-Scripts/MPRIS-Discord-Presence)*
