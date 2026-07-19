from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from hgpt_ai_os.settings.config_manager import ConfigManager, PROVIDER_KEY_FIELD
from hgpt_ai_os.settings.provider_registry import provider_info


class SettingsDialog(QDialog):
    PROVIDERS = (
        ("OpenAI", "openai"),
        ("Google Gemini (Coming Soon)", "gemini"),
        ("Claude (Coming Soon)", "anthropic"),
        ("Ollama (Coming Soon)", "ollama"),
    )

    def __init__(self, config_manager: ConfigManager, parent=None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = self.config_manager.load()
        self.current_provider = self.config.get("provider", "openai")

        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(520)

        self.provider_combo = QComboBox()
        for label, value in self.PROVIDERS:
            self.provider_combo.addItem(label, value)
            index = self.provider_combo.count() - 1
            if provider_info(value).coming_soon:
                self.provider_combo.model().item(index).setEnabled(False)

        self.model = QLabel("")
        self.last_successful_test = QLabel("")
        self.masked_key = QLabel("")
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Paste new API key...")

        self.status = QLabel("")
        self.status.setObjectName("connectionStatus")
        self.test_button = QPushButton("Test")
        self.change_key_button = QPushButton("Change API Key")
        self.remove_key_button = QPushButton("Remove API Key")
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

        self._build_layout()
        self._apply_style()
        self._select_provider(self.current_provider)
        self._refresh_provider_fields()

        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        self.test_button.clicked.connect(self._test_connection)
        self.change_key_button.clicked.connect(self._change_api_key)
        self.remove_key_button.clicked.connect(self._remove_api_key)
        self.buttons.accepted.connect(self._save)
        self.buttons.rejected.connect(self.reject)

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(16)

        title = QLabel("AI Provider")
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
        form.addRow("Connected Model", self.model)
        form.addRow("Connection Status", self.status)
        form.addRow("Last Successful Test", self.last_successful_test)
        form.addRow("Masked API Key", self.masked_key)
        form.addRow("New API Key", self.api_key)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        action_row.addWidget(self.test_button)
        action_row.addWidget(self.change_key_button)
        action_row.addWidget(self.remove_key_button)
        action_row.addStretch(1)

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addLayout(action_row)
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
                color: #6f3f00;
            }
            """
        )

    def _select_provider(self, provider: str) -> None:
        index = self.provider_combo.findData(provider)
        self.provider_combo.setCurrentIndex(index if index >= 0 else 0)

    def _current_provider(self) -> str:
        return self.provider_combo.currentData()

    def _on_provider_changed(self) -> None:
        self._sync_current_key()
        self.current_provider = self._current_provider()
        self._refresh_provider_fields()

    def _refresh_provider_fields(self) -> None:
        provider = self._current_provider()
        info = provider_info(provider)
        self.model.setText(info.default_model)
        self.last_successful_test.setText(self.config.get(f"{provider}_last_successful_test", "Never"))
        self.masked_key.setText(self.config_manager.masked_api_key(provider))
        self.api_key.clear()
        validation = self.config_manager.validate()
        if validation.ok and validation.provider == provider:
            self._set_status("🟢 Connected")
        elif provider_info(provider).coming_soon:
            self._set_status("🟡 Coming Soon")
        else:
            self._set_status("🟡 AI Not Configured")

    def _sync_current_key(self) -> None:
        provider = self._current_provider()
        key = self.api_key.text().strip()
        self.config["provider"] = provider
        if key:
            self.config[PROVIDER_KEY_FIELD[provider]] = key

    def _test_connection(self) -> None:
        provider = self._current_provider()
        key = self.api_key.text().strip() or self.config_manager.api_key(provider)
        self._set_status("Testing...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = self.config_manager.test_connection_for(provider, key)
        finally:
            QApplication.restoreOverrideCursor()

        if result.ok:
            self._set_status(f"✓ Connected - {result.provider} - {result.model}")
            self.model.setText(result.model)
            stamp = self.config_manager.mark_successful_test(provider, result.model)
            self.config = self.config_manager.load()
            self.last_successful_test.setText(stamp)
        else:
            self._set_status(result.message, error=True)

    def _change_api_key(self) -> None:
        self.api_key.setFocus()
        self.api_key.selectAll()

    def _remove_api_key(self) -> None:
        provider = self._current_provider()
        self.config_manager.remove_api_key(provider)
        field = PROVIDER_KEY_FIELD.get(provider)
        if field:
            self.config[field] = ""
        self.api_key.clear()
        self.masked_key.setText("Not configured")
        self._set_status("🟡 AI Not Configured")

    def _save(self) -> None:
        self._sync_current_key()
        if provider_info(self._current_provider()).coming_soon:
            QMessageBox.warning(self, "Coming Soon", "This provider is not enabled in this release.")
            return
        self.config_manager.save(self.config)
        self.accept()

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status.setText(text)
        color = "#7a1f1f" if error else "#0f5132" if "Connected" in text else "#6f3f00"
        self.status.setStyleSheet(f"color: {color};")
