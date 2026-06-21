# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

hiddenimports_common = [
    'pypresence',
    'pypresence.exceptions',
    'minio',
    'minio.error',
    'PIL',
    'PIL.Image',
    'backends.smtc',
    'backends.mpris',
]

hiddenimports_windows = [
    'winsdk.windows.media.control',
    'winsdk.windows.storage.streams',
    'winsdk.windows.foundation',
]

hiddenimports_linux = [
    'dbus',
    'pympris',
]

hiddenimports = hiddenimports_common + (
    hiddenimports_windows if sys.platform == 'win32' else hiddenimports_linux
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('playersIcons', 'playersIcons'),
        ('assets', 'assets'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    icon='assets/icon.ico',
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
