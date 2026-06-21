# 🪟 MusicLocal Discord Presence 🐧

> For English, [go here](README.md).

Affichez ce que vous écoutez sur Discord — avec les pochettes stockées sur votre propre instance MinIO/S3. Fonctionne sur **Windows** (SMTC) et **Linux** (MPRIS), avec Chrome, Spotify, VLC, WACUP, et plus encore.

---

## Fonctionnalités

- Détection automatique de la session multimédia active (SMTC sous Windows, MPRIS sous Linux)
- Support VLC via son interface HTTP intégrée
- Pochettes uploadées sur MinIO/S3 avec cache par déduplication SHA-256
- Discord Rich Presence avec titre, artiste, pochette et barre de progression
- Icône en zone de notification avec indicateur de statut (Qt sous Windows/Linux, GTK sous GNOME)
- **Fenêtre de paramètres** — tout se configure via l'interface, aucun fichier de config à éditer
- Mise à jour automatique : notification quand une nouvelle version est disponible, un clic pour télécharger et installer

---

## Prérequis

- Une application Discord ([portail développeur](https://discord.com/developers/applications))
- Une instance MinIO ou compatible S3 avec un bucket public
- (Optionnel) VLC avec l'interface HTTP activée

---

## Installation

Téléchargez le dernier installeur depuis la page [Releases](https://github.com/Bit-Scripts/MusicLocal-Discord-Presence/releases) et lancez-le. L'application apparaît dans la zone de notification. Faites un clic droit sur l'icône → **Paramètres** pour configurer.

### Depuis les sources

```bash
git clone https://github.com/Bit-Scripts/MusicLocal-Discord-Presence.git
cd MusicLocal-Discord-Presence

# Windows
pip install -r requirements-windows.txt

# Linux
pip install -r requirements-linux.txt

python main.py
```

---

## Configuration

Tous les réglages se font dans la **fenêtre Paramètres**, accessible via un clic droit sur l'icône de la zone de notification.

![Fenêtre Paramètres](assets/settings.png)

| Champ | Description | Où le trouver |
|---|---|---|
| **Discord Client ID** | L'identifiant client de votre application Discord | [discord.com/developers/applications](https://discord.com/developers/applications) → votre app → OAuth2 → Client ID |
| **MinIO URL** | Adresse de votre serveur MinIO (sans `https://`) | Panneau d'administration MinIO/TrueNAS, ex. `minio.example.com` |
| **MinIO Access Key** | Clé d'accès MinIO | Console MinIO → Access Keys |
| **MinIO Secret Key** | Clé secrète MinIO | Console MinIO → Access Keys (affichée une seule fois à la création) |
| **MinIO Bucket** | Nom du bucket pour stocker les pochettes | Créez un bucket public dans la console MinIO, ex. `coversimage` |
| **VLC Hôte** | Hôte de l'interface HTTP VLC | Laissez `localhost` si VLC est sur la même machine |
| **VLC Port** | Port de l'interface HTTP VLC | Par défaut `8080` |
| **VLC Mot de passe** | Mot de passe de l'interface HTTP VLC | VLC → Outils → Préférences → Interface → Mot de passe Lua HTTP |

Les paramètres sont sauvegardés automatiquement dans `%APPDATA%\MusicPresence\` (Windows) ou `~/.config/MusicPresence/` (Linux).

---

## Configuration de l'application Discord

1. Aller sur [discord.com/developers/applications](https://discord.com/developers/applications)
2. Créer une nouvelle application
3. Copier le **Client ID** et le coller dans la fenêtre Paramètres
4. Aller dans **Rich Presence → Art Assets** et uploader les icônes des lecteurs avec ces noms : `chrome`, `spotify`, `vlc`, `wacup`, `default_icon`

---

## Configuration de VLC

1. Ouvrir VLC → Outils → Préférences → afficher **Tout**
2. Interface → Interfaces principales → cocher **Web**
3. Interface → Interfaces principales → Lua → définir un **mot de passe Lua HTTP**
4. Redémarrer VLC
5. Saisir le mot de passe dans la fenêtre Paramètres sous **VLC Mot de passe**

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
