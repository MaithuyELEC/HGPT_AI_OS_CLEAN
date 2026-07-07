from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from hgpt_ai_os.settings.config_manager import ConfigManager, PROVIDER_KEY_FIELD


class SettingsDialog(QDialog):
    PROVIDERS = (
        ("Gemini", "gemini"),
        ("OpenAI", "openai"),
        ("Anthropic", "anthropic"),
    )

    def __init__(self, config_manager: ConfigManager, parent=None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = self.config_manager.load()

        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.setMinimumWidth(460)

        self.provider_combo = QComboBox()
        for label, value in self.PROVIDERS:
            self.provider_combo.addItem(label, value)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Paste API key...")
        self.api_key.setMinimumWidth(280)

        self.show_key = QCheckBox("Show")
        self.status = QLabel("Disconnected")
        self.status.setObjectName("connectionStatus")
        self.latency = QLabel("")
        self.latency.setObjectName("latency")
        self.current_provider = self.config.get("provider", "gemini")

        self.test_button = QPushButton("Test Connection")
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

        self._build_layout()
        self._apply_style()
        self._select_provider(self.config.get("provider", "gemini"))
        self._load_key_for_provider()
        self.current_provider = self._current_provider()

        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        self.show_key.toggled.connect(self._toggle_key_visibility)
        self.test_button.clicked.connect(self._test_connection)
        self.buttons.accepted.connect(self._save)
        self.buttons.rejected.connect(self.reject)

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(16)

        title = QLabel("Preferences")
        title.setObjectName("title")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.addRow("Provider", self.provider_combo)

        key_row = QHBoxLayout()
        key_row.setSpacing(8)
        key_row.addWidget(self.api_key, 1)
        key_row.addWidget(self.show_key)
        form.addRow("API Key", key_row)

        status_row = QVBoxLayout()
        status_row.setSpacing(2)
        status_row.addWidget(self.status)
        status_row.addWidget(self.latency)
        form.addRow("Status", status_row)

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(self.test_button, 0, Qt.AlignLeft)
        layout.addWidget(self.buttons)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background: #f7fafc;
                color: #1f2933;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                font-size: 13px;
            }
            QLabel#title {
                color: #102a43;
            }
            QComboBox,
            QLineEdit {
                min-height: 34px;
                padding: 0 10px;
                color: #1f2933;
                background: #ffffff;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
            }
            QPushButton {
                min-height: 34px;
                padding: 0 16px;
                color: #19364d;
                background: #eef3f7;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
                font-weight: 700;
            }
            QLabel#connectionStatus {
                font-weight: 800;
                color: #7a1f1f;
            }
            QLabel#latency {
                color: #52606d;
                font-size: 12px;
            }
            """
        )

    def _select_provider(self, provider: str) -> None:
        index = self.provider_combo.findData(provider)
        self.provider_combo.setCurrentIndex(index if index >= 0 else 0)

    def _current_provider(self) -> str:
        return self.provider_combo.currentData()

    def _load_key_for_provider(self) -> None:
        provider = self._current_provider()
        self.api_key.setText(self.config.get(PROVIDER_KEY_FIELD[provider], ""))
        self._set_status("Disconnected")

    def _on_provider_changed(self) -> None:
        self._sync_key_for_provider(self.current_provider)
        self.current_provider = self._current_provider()
        self._load_key_for_provider()

    def _sync_current_key(self) -> None:
        provider = self._current_provider()
        self._sync_key_for_provider(provider)

    def _sync_key_for_provider(self, provider: str) -> None:
        self.config["provider"] = provider
        self.config[PROVIDER_KEY_FIELD[provider]] = self.api_key.text().strip()

    def _toggle_key_visibility(self, checked: bool) -> None:
        self.api_key.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def _test_connection(self) -> None:
        self._sync_current_key()
        self.config_manager.save(self.config)
        self._set_status("Testing...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = self.config_manager.test_connection()
        finally:
            QApplication.restoreOverrideCursor()

        self._set_status(result.status if result.ok else result.message)
        if result.latency_ms is None:
            self.latency.setText(result.reason)
        else:
            self.latency.setText(f"Latency: {result.latency_ms} ms")

    def _save(self) -> None:
        self._sync_current_key()
        self.config_manager.save(self.config)
        self.accept()

    def _set_status(self, text: str) -> None:
        self.status.setText(text)
        color = "#0f5132" if text == "Connected" else "#7a1f1f"
        self.status.setStyleSheet(f"color: {color};")
