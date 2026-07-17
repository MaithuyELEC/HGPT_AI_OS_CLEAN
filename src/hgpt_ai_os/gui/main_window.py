from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QSize, QSettings, Qt, qVersion
from PySide6.QtGui import (
    QAction,
    QFont,
    QKeySequence,
    QShortcut,
    QTextBlockFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

from hgpt_ai_os.core.production_result import ProductionResult
from hgpt_ai_os.diagnostics import module_loaded, trace_call
from hgpt_ai_os.settings import ConfigManager
from hgpt_ai_os.settings.settings_dialog import SettingsDialog
from hgpt_ai_os.version import APP_BUILD as RELEASE_BUILD
from hgpt_ai_os.version import APP_VERSION as RELEASE_VERSION

from .branding import APP_DISPLAY_NAME, APP_POWERED_BY, app_icon
from .worker import ProductionWorker


class MainWindow(QMainWindow):
    MAX_TOPIC_HISTORY = 10
    APP_VERSION = RELEASE_VERSION
    APP_BUILD = RELEASE_BUILD

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setWindowIcon(app_icon())
        self.resize(1040, 720)
        self.setMinimumSize(960, 660)

        self.worker = None
        self.production_result = None
        self.settings = QSettings("MaithuyELEC", "Lucid AI Studio")
        self.topic_history = self._load_topic_history()
        self.last_output_folder = self.settings.value("last_output_folder", "", str)
        self.auto_open_output_folder = self.settings.value(
            "auto_open_output_folder", False, bool
        )
        self.total_jobs_generated = int(
            self.settings.value("total_jobs_generated", 0, int)
        )
        self.config_manager = ConfigManager()
        self.config_manager.load()
        self.shortcuts = []

        self._build_menu()

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 22, 24, 16)
        layout.setSpacing(16)

        self._build_header(layout)
        self._build_input_area(layout)
        self._build_status_area(layout)
        self._build_progress_area(layout)
        self._build_console_area(layout)
        self._build_summary_area(layout)
        self._build_generated_files_area(layout)
        self._build_output_area(layout)
        self._apply_theme()

        self.btn.clicked.connect(self.generate)
        self.clear_btn.clicked.connect(self.clear_console)
        self.output_btn.clicked.connect(self.open_output_folder)
        self._install_shortcuts()
        self._restore_last_output_folder()
        self._restore_window_state()
        self._log_configuration_status()
        self._refresh_ai_status()

    def _build_menu(self):
        preferences_menu = self.menuBar().addMenu("Preferences")

        ai_settings_action = QAction("AI Settings", self)
        ai_settings_action.triggered.connect(self.open_ai_settings)
        preferences_menu.addAction(ai_settings_action)
        preferences_menu.addSeparator()

        self.auto_open_action = QAction("Auto Open Output Folder", self)
        self.auto_open_action.setCheckable(True)
        self.auto_open_action.setChecked(self.auto_open_output_folder)
        self.auto_open_action.toggled.connect(self._set_auto_open_output_folder)
        preferences_menu.addAction(self.auto_open_action)

        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction(f"About {APP_DISPLAY_NAME}", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _build_header(self, layout):
        header = QFrame()
        header.setObjectName("header")
        header.setMinimumHeight(132)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        header_layout = QGridLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)
        header_layout.setHorizontalSpacing(18)
        header_layout.setVerticalSpacing(6)

        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("appTitle")
        title.setMinimumHeight(42)
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        platform_label = QLabel("AI Engineering Platform")
        platform_label.setObjectName("platformLabel")
        platform_label.setMinimumHeight(20)
        platform_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        powered_by = QLabel(APP_POWERED_BY)
        powered_by.setObjectName("poweredBy")
        powered_by.setMinimumHeight(18)
        powered_by.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        version = QLabel(f"✅ Production\n{self.APP_VERSION}")
        version.setObjectName("version")
        version.setMinimumSize(140, 66)
        version.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title, 0, 0)
        header_layout.addWidget(platform_label, 1, 0)
        header_layout.addWidget(powered_by, 2, 0)
        header_layout.addWidget(version, 0, 1, 3, 1)
        header_layout.setRowMinimumHeight(0, 42)
        header_layout.setRowMinimumHeight(1, 20)
        header_layout.setRowMinimumHeight(2, 18)
        header_layout.setColumnStretch(0, 1)

        layout.addWidget(header)

    def _build_input_area(self, layout):
        panel = QFrame()
        panel.setObjectName("panel")
        row = QHBoxLayout(panel)
        row.setContentsMargins(18, 16, 18, 16)
        row.setSpacing(12)

        label = QLabel("Topic")
        label.setObjectName("fieldLabel")

        self.topic = QComboBox()
        self.topic.setEditable(True)
        self.topic.setPlaceholderText("Enter production topic...")
        self.topic.addItems(self.topic_history)
        self.topic.lineEdit().setClearButtonEnabled(True)
        self.topic.lineEdit().returnPressed.connect(self.generate)

        self.btn = QPushButton("🚀  Generate")
        self.btn.setObjectName("primaryButton")
        self.btn.setMinimumSize(148, 44)

        self.clear_btn = QPushButton("🧹  Clear")
        self.clear_btn.setMinimumWidth(96)

        row.addWidget(label)
        row.addWidget(self.topic, 1)
        row.addWidget(self.btn)
        row.addWidget(self.clear_btn)

        layout.addWidget(panel)

    def _build_status_area(self, layout):
        panel = QFrame()
        panel.setObjectName("statusPanel")
        row = QHBoxLayout(panel)
        row.setContentsMargins(18, 12, 18, 12)
        row.setSpacing(12)

        self.engine_status = QLabel("Ready")
        self.engine_status.setObjectName("engineStatus")

        self.run_status = QLabel("Ready")
        self.run_status.setObjectName("runStatus")
        self._set_status_badge(self.engine_status, "ready", "Ready")
        self._set_status_badge(self.run_status, "ready", "Ready")

        row.addWidget(self.engine_status)
        row.addStretch(1)
        row.addWidget(self.run_status)

        layout.addWidget(panel)

    def _build_progress_area(self, layout):
        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.hide()

        layout.addWidget(self.progress)

    def _build_console_area(self, layout):
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setLineWrapMode(QTextEdit.NoWrap)
        console_font = QFont("Menlo", 12)
        console_font.setStyleHint(QFont.Monospace)
        console_font.setFixedPitch(True)
        console_font.setStyleStrategy(QFont.PreferAntialias)
        self.console.setFont(console_font)
        self.console.document().setDocumentMargin(6)
        self.console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._set_console_text(
            "==================================================\n"
            f"Lucid AI Studio {self.APP_VERSION}\n"
            "Production Ready\n"
            "\n"
            "Ready to generate production content.\n"
            "=================================================="
        )

        layout.addWidget(self.console, 1)

    def _build_summary_area(self, layout):
        self.summary_panel = QFrame()
        self.summary_panel.setObjectName("summaryPanel")
        summary_layout = QGridLayout(self.summary_panel)
        summary_layout.setContentsMargins(18, 14, 18, 14)
        summary_layout.setHorizontalSpacing(18)
        summary_layout.setVerticalSpacing(8)

        title = QLabel("Job Summary")
        title.setObjectName("summaryTitle")

        self.summary_topic = QLabel("—")
        self.summary_status = QLabel("—")
        self.summary_knowledge = QLabel("—")
        self.summary_output = QLabel("—")
        self.summary_elapsed = QLabel("—")
        self.summary_total_jobs = QLabel(str(self.total_jobs_generated))

        values = (
            ("Topic", self.summary_topic),
            ("Status", self.summary_status),
            ("Knowledge", self.summary_knowledge),
            ("Elapsed Time", self.summary_elapsed),
            ("Output Folder", self.summary_output),
            ("Total Jobs Generated", self.summary_total_jobs),
        )

        summary_layout.addWidget(title, 0, 0, 1, 4)

        for index, (label_text, value_widget) in enumerate(values, start=1):
            label = QLabel(label_text)
            label.setObjectName("summaryLabel")
            value_widget.setObjectName("summaryValue")

            row = 1 + (index - 1) // 2
            column = 0 if index % 2 else 2

            summary_layout.addWidget(label, row, column)
            summary_layout.addWidget(value_widget, row, column + 1)

        summary_layout.setColumnStretch(1, 1)
        summary_layout.setColumnStretch(3, 1)
        self.summary_panel.hide()

        layout.addWidget(self.summary_panel)

    def _build_generated_files_area(self, layout):
        self.files_panel = QFrame()
        self.files_panel.setObjectName("filesPanel")
        files_layout = QVBoxLayout(self.files_panel)
        files_layout.setContentsMargins(18, 14, 18, 14)
        files_layout.setSpacing(8)

        self.files_title = QLabel("Generated Files (0)")
        self.files_title.setObjectName("summaryTitle")

        self.files_list = QListWidget()
        self.files_list.setObjectName("filesList")
        self.files_list.setMinimumHeight(132)
        self.files_list.setMaximumHeight(176)
        self.files_list.setSpacing(3)
        self.files_list.setIconSize(QSize(22, 22))
        self.files_list.itemDoubleClicked.connect(self.open_generated_file)

        files_layout.addWidget(self.files_title)
        files_layout.addWidget(self.files_list)
        self.files_panel.hide()

        layout.addWidget(self.files_panel)

    def _build_output_area(self, layout):
        panel = QFrame()
        panel.setObjectName("outputPanel")
        row = QHBoxLayout(panel)
        row.setContentsMargins(18, 12, 18, 12)
        row.setSpacing(12)

        label = QLabel("Output Root")
        label.setObjectName("fieldLabel")

        self.output_path = QLabel("~/Documents/Lucid AI Studio/outputs/marketing")
        self.output_path.setObjectName("outputPath")

        self.output_btn = QPushButton("📂  Open Output Folder")
        self.output_btn.setObjectName("secondaryButton")
        self.output_btn.setMinimumSize(184, 40)

        row.addWidget(label)
        row.addWidget(self.output_path, 1)
        row.addWidget(self.output_btn)

        layout.addWidget(panel)

    def _apply_theme(self):
        self.setStyleSheet(
            """
            QWidget#root {
                background: #f4f7fa;
                color: #1f2933;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                font-size: 13px;
            }
            QFrame#header {
                background: #fbfcfd;
                border: 1px solid #c4d0dc;
                border-radius: 8px;
            }
            QLabel#appTitle {
                color: #102a43;
                font-size: 31px;
                font-weight: 800;
                letter-spacing: 0px;
            }
            QLabel#platformLabel {
                color: #52606d;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#poweredBy {
                color: #19364d;
                font-size: 13px;
                font-weight: 700;
            }
            QLabel#factoryCaption {
                color: #71808f;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#version {
                color: #102a43;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 16px;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
                background: #eef4f8;
                qproperty-alignment: AlignCenter;
            }
            QFrame#panel,
            QFrame#statusPanel,
            QFrame#summaryPanel,
            QFrame#filesPanel,
            QFrame#outputPanel {
                background: #ffffff;
                border: 1px solid #d5dee7;
                border-radius: 8px;
            }
            QLabel#summaryTitle {
                color: #19364d;
                font-size: 14px;
                font-weight: 800;
            }
            QLabel#summaryLabel {
                color: #71808f;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#summaryValue {
                color: #1f2933;
                font-size: 13px;
                font-weight: 600;
            }
            QListWidget#filesList {
                color: #1f2933;
                background: #f8fafc;
                border: 1px solid #d5dee7;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                font-weight: 650;
            }
            QListWidget#filesList::item {
                min-height: 30px;
                padding: 7px 10px;
                border-radius: 5px;
            }
            QListWidget#filesList::item:hover {
                background: #edf4f8;
            }
            QListWidget#filesList::item:selected {
                color: #ffffff;
                background: #2f5f7f;
                border-radius: 5px;
            }
            QListWidget#filesList QScrollBar:vertical,
            QTextEdit#console QScrollBar:vertical {
                background: #e6edf3;
                width: 12px;
                margin: 2px;
                border-radius: 6px;
            }
            QListWidget#filesList QScrollBar::handle:vertical,
            QTextEdit#console QScrollBar::handle:vertical {
                background: #a8bac9;
                min-height: 28px;
                border-radius: 6px;
            }
            QListWidget#filesList QScrollBar::handle:vertical:hover,
            QTextEdit#console QScrollBar::handle:vertical:hover {
                background: #7f98aa;
            }
            QListWidget#filesList QScrollBar::add-line:vertical,
            QListWidget#filesList QScrollBar::sub-line:vertical,
            QTextEdit#console QScrollBar::add-line:vertical,
            QTextEdit#console QScrollBar::sub-line:vertical {
                height: 0;
                border: 0;
            }
            QLabel#fieldLabel {
                color: #334e68;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
            }
            QLineEdit,
            QComboBox {
                min-height: 36px;
                padding: 0 12px;
                color: #1f2933;
                background: #ffffff;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
                selection-background-color: #2f5f7f;
            }
            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #2f5f7f;
                background: #fbfdff;
            }
            QComboBox::drop-down {
                border: 0;
                width: 26px;
            }
            QPushButton {
                min-height: 38px;
                padding: 0 18px;
                color: #19364d;
                background: #eef3f7;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #e2ebf2;
            }
            QPushButton:pressed {
                background: #d5e1ea;
            }
            QPushButton:disabled {
                color: #8a99a8;
                background: #eef1f4;
                border-color: #d5dee7;
            }
            QPushButton#primaryButton {
                min-height: 44px;
                color: #ffffff;
                background: #245a78;
                border-color: #1f4b65;
                font-size: 14px;
                padding: 0 22px;
            }
            QPushButton#primaryButton:hover {
                background: #1e6b8f;
                border-color: #174f6a;
            }
            QPushButton#secondaryButton {
                background: #f7fafc;
                border-color: #aebdca;
            }
            QPushButton#secondaryButton:hover {
                background: #eaf2f7;
                border-color: #8fa5b7;
            }
            QLabel#engineStatus {
                border-radius: 12px;
                padding: 5px 12px;
                font-weight: 800;
            }
            QLabel#engineStatus[status="ready"],
            QLabel#engineStatus[status="connected"] {
                color: #0f5132;
                background: #e7f4ec;
                border: 1px solid #a7d7bd;
            }
            QLabel#engineStatus[status="disconnected"],
            QLabel#engineStatus[status="config_error"] {
                color: #7a1f1f;
                background: #fbe7e7;
                border: 1px solid #e2aaaa;
            }
            QLabel#runStatus {
                border-radius: 12px;
                padding: 5px 12px;
                font-weight: 700;
            }
            QLabel#runStatus[status="ready"] {
                color: #38546a;
                background: #eef4f8;
                border: 1px solid #c4d0dc;
            }
            QLabel#runStatus[status="running"] {
                color: #6f3f00;
                background: #fff1d6;
                border: 1px solid #e3b45b;
            }
            QLabel#runStatus[status="generating"] {
                color: #6f3f00;
                background: #fff1d6;
                border: 1px solid #e3b45b;
            }
            QLabel#runStatus[status="exporting"] {
                color: #17406f;
                background: #e5f0ff;
                border: 1px solid #9fc3ef;
            }
            QLabel#runStatus[status="completed"] {
                color: #0f5132;
                background: #e7f4ec;
                border: 1px solid #a7d7bd;
            }
            QLabel#runStatus[status="error"] {
                color: #7a1f1f;
                background: #fbe7e7;
                border: 1px solid #e2aaaa;
            }
            QLabel#runStatus[status="config_error"] {
                color: #7a1f1f;
                background: #fbe7e7;
                border: 1px solid #e2aaaa;
            }
            QProgressBar#progress {
                background: #d5dee7;
                border: 0;
                border-radius: 4px;
            }
            QProgressBar#progress::chunk {
                background: #2f5f7f;
                border-radius: 4px;
            }
            QTextEdit#console {
                color: #dbe7ef;
                background: #111820;
                border: 1px solid #25313c;
                border-radius: 8px;
                padding: 14px;
                font-family: Menlo, Consolas, monospace;
                font-size: 13px;
                selection-background-color: #2f5f7f;
            }
            QLabel#outputPath {
                color: #1f2933;
                font-family: Menlo, Consolas, monospace;
                background: #f4f7fa;
                border: 1px solid #d5dee7;
                border-radius: 6px;
                padding: 8px 10px;
            }
            """
        )

    def _set_status_badge(self, label, status: str, text: str):
        label.setText(text)
        label.setProperty("status", status)
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()

    def _install_shortcuts(self):
        for sequence in ("Ctrl+Return", "Ctrl+Enter", "Meta+Return", "Meta+Enter"):
            shortcut = QKeySequence(sequence)
            if not shortcut.isEmpty():
                self.shortcuts.append(QShortcut(shortcut, self, self.generate))

    def _load_topic_history(self):
        value = self.settings.value("topic_history", [], list)
        if isinstance(value, str):
            value = [value]
        return [topic for topic in value if topic][: self.MAX_TOPIC_HISTORY]

    def _save_topic(self, topic):
        self.topic_history = [
            topic,
            *[item for item in self.topic_history if item != topic],
        ][: self.MAX_TOPIC_HISTORY]
        self.settings.setValue("topic_history", self.topic_history)
        self.topic.blockSignals(True)
        self.topic.clear()
        self.topic.addItems(self.topic_history)
        self.topic.setCurrentText(topic)
        self.topic.blockSignals(False)

    def _restore_last_output_folder(self):
        if self.last_output_folder:
            self.output_path.setText(self.last_output_folder)

    def _save_last_output_folder(self, output_dir):
        if output_dir is None:
            return

        self.last_output_folder = str(output_dir)
        self.settings.setValue("last_output_folder", self.last_output_folder)
        self.output_path.setText(self.last_output_folder)

    def _increment_total_jobs(self):
        self.total_jobs_generated += 1
        self.settings.setValue("total_jobs_generated", self.total_jobs_generated)
        self.summary_total_jobs.setText(str(self.total_jobs_generated))

    def _set_auto_open_output_folder(self, enabled):
        self.auto_open_output_folder = enabled
        self.settings.setValue("auto_open_output_folder", enabled)

    def _restore_window_state(self):
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self.settings.setValue("window_geometry", self.saveGeometry())
        super().closeEvent(event)

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            f"About {APP_DISPLAY_NAME}",
            "\n".join(
                (
                    APP_DISPLAY_NAME,
                    "Version 1.0.0",
                    APP_POWERED_BY,
                )
            ),
        )

    def open_ai_settings(self):
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec() == SettingsDialog.Accepted:
            self._log_configuration_status()
            self._refresh_ai_status()

    def _log_configuration_status(self):
        validation = self.config_manager.validate()
        self.append_console("")
        self.append_console("Loading configuration...")
        self.append_console(f"Provider: {validation.provider.title()}")
        if validation.ok:
            self.append_console("Connection OK")
        else:
            self.append_console("Connection Error")

    def _refresh_ai_status(self):
        validation = self.config_manager.validate()
        if validation.ok:
            self._set_status_badge(
                self.engine_status,
                "connected",
                validation.provider.title(),
            )
        else:
            self._set_status_badge(self.engine_status, "disconnected", "Disconnected")

    def generate(self):
        trace_call(
            "Generate Button",
            self,
            selected_topic=self.topic.currentText().strip(),
            selected_domain="n/a",
            selected_playbook="n/a",
            writer_selected="ProductionWorker",
            writer_class=ProductionWorker.__name__,
            knowledge_count="pending",
            output_file="pending",
        )
        if self.worker is not None and self.worker.isRunning():
            return

        topic = self.topic.currentText().strip()

        if not topic:
            self._set_status_badge(self.run_status, "ready", "Ready")
            self.append_console("Warning: Topic is required before generation.")
            QMessageBox.warning(
                self,
                "Topic Required",
                "Please enter a topic before starting production.",
            )
            self.topic.setFocus()
            return

        validation = self.config_manager.validate()
        if not validation.ok:
            self.console.clear()
            self.summary_panel.hide()
            self.files_panel.hide()
            self.production_result = None
            self._set_status_badge(self.run_status, "config_error", "Configuration Error")
            self._set_status_badge(self.engine_status, "config_error", "Configuration Error")
            self.append_console("Loading configuration...")
            self.append_console(validation.message)
            self.append_console("Status: Configuration Error")
            if validation.reason:
                self.append_console(f"Reason: {validation.reason}")
            self.append_console(f"Provider: {validation.provider.title()}")
            reply = QMessageBox.question(
                self,
                "AI is not configured.",
                "AI is not configured.\n\nOpen Settings now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self.open_ai_settings()
                validation = self.config_manager.validate()
                if not validation.ok:
                    return
            else:
                return

        self._save_topic(topic)
        self.console.clear()
        self.summary_panel.hide()
        self.files_panel.hide()
        self.production_result = None
        self._set_status_badge(
            self.engine_status,
            "connected",
            validation.provider.title(),
        )
        self._set_status_badge(self.run_status, "generating", "Generating")
        self.append_console("Loading configuration...")
        self.append_console(f"Provider: {validation.provider.title()}")
        self.append_console("Connection OK")
        self.append_console("Generation Started")

        self.progress.show()
        self.set_controls_enabled(False)

        self.worker = ProductionWorker(topic)

        self.worker.log.connect(self.handle_worker_log)
        self.worker.finished.connect(self.finished)
        self.worker.finished.connect(self.worker.deleteLater)

        self.worker.start()

    def finished(self, result):
        self.worker = None
        self.progress.hide()
        self.set_controls_enabled(True)

        if not isinstance(result, ProductionResult):
            result = ProductionResult(
                success=False,
                output_dir=None,
                generated_files=[],
                knowledge_count=None,
                elapsed_seconds=None,
            )

        self.production_result = result

        if result.success:
            self._set_status_badge(self.run_status, "exporting", "Exporting DOCX...")
            self._increment_total_jobs()
            self._save_last_output_folder(result.output_dir)
            self.update_summary(result)
            self.update_generated_files(result)
            self._set_status_badge(self.run_status, "completed", "Completed.")
            self.append_console("")
            self.append_console("==========")
            self.append_console("Production Completed")
            if result.output_dir is None or not Path(result.output_dir).exists():
                QMessageBox.warning(
                    self,
                    "Output Folder Not Found",
                    "The output folder could not be found.",
                )
            elif self.auto_open_output_folder:
                self.open_output_folder()
            QMessageBox.information(
                self,
                "Production Completed",
                "Production completed successfully.",
            )
        else:
            self._set_status_badge(self.run_status, "error", "Error")
            self.append_console("")
            self.append_console("==========")
            self.append_console("Production Failed")
            QMessageBox.critical(
                self,
                "Production Failed",
                "Production could not be completed. Please try again or contact support.",
            )

        

    def clear_console(self):
        self.console.clear()
        self._set_console_text(
            "==================================================\n"
            f"Lucid AI Studio {self.APP_VERSION}\n"
            "Production Ready\n"
            "\n"
            "Ready to generate production content.\n"
            "=================================================="
        )
        self._set_status_badge(self.run_status, "ready", "Ready")
        self.summary_panel.hide()
        self.files_panel.hide()
        self.files_title.setText("Generated Files (0)")

    def _set_console_text(self, text: str):
        self.console.setPlainText(text)
        self._apply_console_spacing()
        self.console.moveCursor(QTextCursor.End)

    def _apply_console_spacing(self):
        cursor = QTextCursor(self.console.document())
        cursor.select(QTextCursor.Document)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(135.0, QTextBlockFormat.ProportionalHeight.value)
        block_format.setBottomMargin(3)
        cursor.setBlockFormat(block_format)

    def handle_worker_log(self, text):
        self.update_run_status_from_log(text)
        self.append_console(text)

    def update_run_status_from_log(self, text):
        if "[01/08]" in text:
            self._set_status_badge(self.run_status, "running", "Analyzing topic...")
        elif "[02/08]" in text:
            self._set_status_badge(self.run_status, "running", "Searching knowledge...")
        elif "[03/08]" in text or "[04/08]" in text:
            self._set_status_badge(self.run_status, "running", "Ranking...")
        elif "[05/08]" in text or "[06/08]" in text:
            self._set_status_badge(self.run_status, "running", "Generating AI content...")
        elif "[07/08]" in text:
            self._set_status_badge(self.run_status, "exporting", "Exporting DOCX...")
        elif "[08/08]" in text or "STATUS    : PRODUCTION SUCCESS" in text:
            self._set_status_badge(self.run_status, "completed", "Completed.")

    def append_console(self, text):
        self.console.append(text)
        self._apply_console_spacing()
        self.console.moveCursor(QTextCursor.End)

    def set_controls_enabled(self, enabled):
        self.topic.setEnabled(enabled)
        self.btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.output_btn.setEnabled(True)
        self.files_list.setEnabled(True)

    def update_summary(self, result: ProductionResult):
        self.summary_topic.setText(self.topic.currentText().strip() or "—")
        self.summary_status.setText("Completed")
        self.summary_knowledge.setText(
            "—" if result.knowledge_count is None else str(result.knowledge_count)
        )
        self.summary_elapsed.setText(
            "—"
            if result.elapsed_seconds is None
            else f"{result.elapsed_seconds:.2f} seconds"
        )
        self.summary_output.setText(
            "—" if result.output_dir is None else str(result.output_dir)
        )
        self.summary_panel.show()

    def update_generated_files(self, result: ProductionResult):
        self.files_list.clear()
        generated_count = len(result.generated_files)
        self.files_title.setText(f"Generated Files ({generated_count})")

        if not result.generated_files:
            item = QListWidgetItem("No generated documents.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)
            self.files_list.addItem(item)
        else:
            for document in result.generated_files:
                item = QListWidgetItem(
                    f"{self._document_icon(document.name)}  {document.name}"
                )
                item.setData(Qt.UserRole, str(document))
                item.setToolTip(str(document))
                self.files_list.addItem(item)
            self.files_list.setCurrentRow(0)

        self.files_panel.show()

    def _document_icon(self, filename: str) -> str:
        name = filename.lower()
        if "facebook" in name:
            return "📘"
        if "hashtag" in name:
            return "🏷"
        if "image" in name:
            return "🖼"
        if "video" in name:
            return "🎬"
        if "seo" in name:
            return "🔍"
        if "approval" in name or "checklist" in name:
            return "✅"
        return "📄"

    def open_generated_file(self, item):
        path = item.data(Qt.UserRole)

        if not path:
            return

        document = Path(path)

        if not document.exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                "The selected generated file could not be found.",
            )
            return

        self._open_path(document, "File Open Failed")

    def open_output_folder(self):
        if self.production_result is not None:
            output = self.production_result.output_dir
        elif self.last_output_folder:
            output = Path(self.last_output_folder)
        else:
            return

        if output is None or not output.exists():
            QMessageBox.warning(
                self,
                "Output Folder Not Found",
                "The output folder could not be found.",
            )
            return

        self._open_path(output, "Output Folder Open Failed")

    def _open_path(self, path: Path, title: str):
        try:
            system = platform.system()

            if system == "Darwin":
                subprocess.Popen(["open", str(path)])
            elif system == "Windows":
                os.startfile(str(path))
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except OSError as exc:
            QMessageBox.warning(
                self,
                title,
                f"Could not open:\n{path}\n\n{exc}",
            )


module_loaded(__name__, __file__, MainWindow)
