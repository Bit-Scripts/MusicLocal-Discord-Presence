import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QGroupBox, QVBoxLayout,
)
from PyQt6.QtCore import Qt
from dotenv import dotenv_values, set_key
from config import ENV_PATH

FIELDS = [
    ('DISCORD_CLIENT_ID', 'Discord Client ID',  '1169241743561080883', False),
    ('MINIO_URL',         'MinIO URL',           'minio.example.com',   False),
    ('MINIO_ACCESS_KEY',  'MinIO Access Key',    '',                    False),
    ('MINIO_SECRET_KEY',  'MinIO Secret Key',    '',                    True),
    ('MINIO_BUCKET',      'MinIO Bucket',        'coversimage',         False),
    ('VLC_HOST',          'VLC Hôte',            'localhost',           False),
    ('VLC_PORT',          'VLC Port',            '8080',                False),
    ('VLC_PASSWORD',      'VLC Mot de passe',    '',                    True),
]


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('MusicLocal Presence — Paramètres')
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self._inputs = {}
        values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}

        layout = QVBoxLayout(self)

        discord_group = QGroupBox('Discord')
        discord_form = QFormLayout(discord_group)
        self._add_field(discord_form, values, *FIELDS[0])
        layout.addWidget(discord_group)

        minio_group = QGroupBox('MinIO / S3')
        minio_form = QFormLayout(minio_group)
        for field in FIELDS[1:5]:
            self._add_field(minio_form, values, *field)
        layout.addWidget(minio_group)

        vlc_group = QGroupBox('VLC (interface HTTP)')
        vlc_form = QFormLayout(vlc_group)
        for field in FIELDS[5:]:
            self._add_field(vlc_form, values, *field)
        layout.addWidget(vlc_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.hide)
        layout.addWidget(buttons)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def _add_field(self, form, values, key, label, placeholder, is_password):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setText(values.get(key, ''))
        if is_password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        self._inputs[key] = field
        form.addRow(label, field)

    def _save(self):
        ENV_PATH.touch(exist_ok=True)
        for key, field in self._inputs.items():
            set_key(str(ENV_PATH), key, field.text())
        self.hide()
