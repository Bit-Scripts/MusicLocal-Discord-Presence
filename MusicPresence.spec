# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

winsdk_datas, winsdk_binaries, winsdk_hiddenimports = ([], [], [])
if sys.platform == 'win32':
    winsdk_datas, winsdk_binaries, winsdk_hiddenimports = collect_all('winsdk')

hiddenimports_common = [
    'pypresence',
    'pypresence.exceptions',
    'minio',
    'minio.error',
    'PIL',
    'PIL.Image',
    'backends.smtc',
    'backends.mpris',
    'config',
    'version',
    'updater',
    'ui.update_dialog',
    'ui.notify',
    'packaging',
    'packaging.version',
]

hiddenimports_windows = [
    'winsdk.windows.media.control',
    'winsdk.windows.storage.streams',
    'winsdk.windows.foundation',
    'winotify',
] + winsdk_hiddenimports

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
    binaries=winsdk_binaries,
    datas=[
        ('playersIcons', 'playersIcons'),
        ('assets', 'assets'),
    ] + winsdk_datas,
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
    [],
    exclude_binaries=True,
    name='MusicPresence',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusicPresence',
)
