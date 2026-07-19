from __future__ import annotations

import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from hgpt_ai_os.settings.config_manager import ConfigManager, PROVIDER_KEY_FIELD
from hgpt_ai_os.settings.provider_registry import PROVIDERS, provider_info


class AISetupWizard(QDialog):
    def __init__(self, config_manager: ConfigManager, parent=None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = self.config_manager.load()
        self.last_test_ok = False
        self.last_test_model = ""

        self.setWindowTitle("AI Setup Wizard")
        self.setModal(True)
        self.setMinimumWidth(520)

        self.provider_group = QButtonGroup(self)
        self.provider_buttons: dict[str, QRadioButton] = {}
        for key in ("openai", "gemini", "anthropic", "ollama"):
            info = provider_info(key)
            label = info.label
            if info.coming_soon:
                label = f"{label} (Coming Soon)"
            button = QRadioButton(label)
            button.setEnabled(not info.coming_soon)
            self.provider_group.addButton(button)
            self.provider_group.setId(button, len(self.provider_buttons))
            self.provider_buttons[key] = button

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Paste API key...")

        self.instructions_button = QPushButton("📖 Hướng dẫn lấy API Key")
        self.open_key_page_button = QPushButton("🌐 Lấy API Key")
        self.test_button = QPushButton("Test Connection")
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.status = QLabel("AI Not Configured")
        self.status.setObjectName("connectionStatus")

        self._build_layout()
        self._apply_style()
        self._select_provider(self.config.get("provider", "openai"))
        self._load_key()

        for key, button in self.provider_buttons.items():
            button.toggled.connect(lambda checked, value=key: checked and self._provider_changed(value))
        self.instructions_button.clicked.connect(self._show_instructions)
        self.open_key_page_button.clicked.connect(self._open_key_page)
        self.test_button.clicked.connect(self._test_connection)
        self.save_button.clicked.connect(self._save)
        self.cancel_button.clicked.connect(self.reject)

    def selected_provider(self) -> str:
        for key, button in self.provider_buttons.items():
            if button.isChecked():
                return key
        return "openai"

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(16)

        title = QLabel("Welcome to Lucid AI Studio")
        title.setObjectName("title")
        subtitle = QLabel("Configure an AI Provider to enable intelligent content generation.")
        subtitle.setWordWrap(True)

        provider_label = QLabel("AI Provider")
        provider_label.setObjectName("fieldLabel")
        key_label = QLabel("API Key")
        key_label.setObjectName("fieldLabel")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(4)
        layout.addWidget(provider_label)
        for key in ("openai", "gemini", "anthropic", "ollama"):
            layout.addWidget(self.provider_buttons[key])
        layout.addSpacing(4)
        layout.addWidget(key_label)
        layout.addWidget(self.api_key)
        layout.addWidget(self.instructions_button)
        layout.addWidget(self.open_key_page_button)
        layout.addWidget(self.status)

        action_row = QHBoxLayout()
        action_row.addWidget(self.test_button)
        action_row.addStretch(1)
        action_row.addWidget(self.cancel_button)
        action_row.addWidget(self.save_button)
        layout.addLayout(action_row)

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
                font-size: 20px;
                font-weight: 800;
            }
            QLabel#fieldLabel {
                color: #334e68;
                font-size: 12px;
                font-weight: 800;
                text-transform: uppercase;
            }
            QLineEdit {
                min-height: 36px;
                padding: 0 10px;
                color: #1f2933;
                background: #ffffff;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
            }
            QPushButton {
                min-height: 34px;
                padding: 0 14px;
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
        self.provider_buttons.get(provider, self.provider_buttons["openai"]).setChecked(True)

    def _provider_changed(self, provider: str) -> None:
        self._load_key()
        self.last_test_ok = False
        self.last_test_model = ""
        self.status.setText("AI Not Configured")
        self.status.setStyleSheet("color: #6f3f00;")

    def _load_key(self) -> None:
        provider = self.selected_provider()
        self.api_key.setText(self.config_manager.api_key(provider))

    def _sync_key(self) -> None:
        provider = self.selected_provider()
        self.config["provider"] = provider
        self.config[PROVIDER_KEY_FIELD[provider]] = self.api_key.text().strip()

    def _show_instructions(self) -> None:
        info = provider_info(self.selected_provider())
        steps = "\n".join(f"{index}.\n{step}" for index, step in enumerate(info.instructions, 1))
        QMessageBox.information(self, f"{info.label} API Key", steps)

    def _open_key_page(self) -> None:
        webbrowser.open(provider_info(self.selected_provider()).key_url)

    def _test_connection(self) -> None:
        self._sync_key()
        self.status.setText("Testing...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = self.config_manager.test_connection_for(
                self.selected_provider(),
                self.api_key.text().strip(),
            )
        finally:
            QApplication.restoreOverrideCursor()

        self.last_test_ok = result.ok
        self.last_test_model = result.model
        if result.ok:
            self.status.setText(
                f"✓ Connected\nProvider: {result.provider}\nModel: {result.model}\nStatus: Ready"
            )
            self.status.setStyleSheet("color: #0f5132;")
        else:
            self.status.setText(result.message)
            self.status.setStyleSheet("color: #7a1f1f;")

    def _save(self) -> None:
        self._sync_key()
        if not self.last_test_ok:
            QMessageBox.warning(
                self,
                "Test Connection Required",
                "Please test the connection successfully before saving.",
            )
            return
        self.config_manager.save(self.config)
        self.accept()

