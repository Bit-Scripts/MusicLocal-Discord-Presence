# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('playersIcons', 'playersIcons'),
    ],
    hiddenimports=[
        # winsdk — chargement dynamique non détecté par PyInstaller
        'winsdk.windows.media.control',
        'winsdk.windows.storage.streams',
        'winsdk.windows.foundation',
        # pypresence
        'pypresence',
        'pypresence.exceptions',
        # minio
        'minio',
        'minio.error',
        # Pillow
        'PIL',
        'PIL.Image',
        # backends
        'backends.smtc',
        'backends.mpris',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclure les dépendances Linux sur Windows et vice versa
        'dbus' if sys.platform == 'win32' else 'winsdk',
        'pympris' if sys.platform == 'win32' else '',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MusicPresence',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Pas de fenêtre CMD
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='playersIcons/default_icon.png',  # décommenter si tu as une icône .ico
)
