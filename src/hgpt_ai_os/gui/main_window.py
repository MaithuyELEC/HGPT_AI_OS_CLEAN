from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

from .worker import ProductionResult, ProductionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LUCID AUTO")
        self.resize(1040, 720)
        self.setMinimumSize(920, 620)

        self.worker = None
        self.production_result = None

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

    def _build_header(self, layout):
        header = QFrame()
        header.setObjectName("header")
        header_layout = QGridLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 18)
        header_layout.setHorizontalSpacing(14)
        header_layout.setVerticalSpacing(4)

        title = QLabel("LUCID AUTO")
        title.setObjectName("appTitle")

        platform_label = QLabel("AI Engineering Platform")
        platform_label.setObjectName("platformLabel")

        powered_by = QLabel("Powered by MaithuyELEC")
        powered_by.setObjectName("poweredBy")

        factory = QLabel("HGPT Steel Digital Factory")
        factory.setObjectName("factoryCaption")

        version = QLabel("Production Ready\nv1.0.0")
        version.setObjectName("version")

        header_layout.addWidget(title, 0, 0)
        header_layout.addWidget(platform_label, 1, 0)
        header_layout.addWidget(powered_by, 2, 0)
        header_layout.addWidget(factory, 3, 0)
        header_layout.addWidget(version, 0, 1, 4, 1)
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

        self.topic = QLineEdit()
        self.topic.setPlaceholderText("Enter production topic...")
        self.topic.setClearButtonEnabled(True)
        self.topic.returnPressed.connect(self.generate)

        self.btn = QPushButton("Generate")
        self.btn.setObjectName("primaryButton")
        self.btn.setMinimumWidth(124)

        self.clear_btn = QPushButton("Clear")
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

        self.engine_status = QLabel("Engine Ready")
        self.engine_status.setObjectName("engineStatus")

        self.run_status = QLabel("Waiting for Topic")
        self.run_status.setObjectName("runStatus")

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
        self.console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.console.setText("Waiting for Topic...")

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

        values = (
            ("Topic", self.summary_topic),
            ("Status", self.summary_status),
            ("Knowledge", self.summary_knowledge),
            ("Elapsed Time", self.summary_elapsed),
            ("Output Folder", self.summary_output),
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

        title = QLabel("Generated Files")
        title.setObjectName("summaryTitle")

        self.files_list = QListWidget()
        self.files_list.setObjectName("filesList")
        self.files_list.setMaximumHeight(96)
        self.files_list.itemDoubleClicked.connect(self.open_generated_file)

        files_layout.addWidget(title)
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

        self.output_path = QLabel("~/Documents/LUCID/outputs/marketing")
        self.output_path.setObjectName("outputPath")

        self.output_btn = QPushButton("Open Output Folder")
        self.output_btn.setMinimumWidth(158)

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
                background: #ffffff;
                border: 1px solid #c7d3df;
                border-radius: 8px;
            }
            QLabel#appTitle {
                color: #19364d;
                font-size: 28px;
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
                color: #19364d;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 12px;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
                background: #eef3f7;
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
                font-size: 13px;
                font-weight: 800;
            }
            QLabel#summaryLabel {
                color: #71808f;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#summaryValue {
                color: #1f2933;
                font-size: 12px;
                font-weight: 600;
            }
            QListWidget#filesList {
                color: #1f2933;
                background: #f4f7fa;
                border: 1px solid #d5dee7;
                border-radius: 6px;
                padding: 4px;
                font-family: "SF Mono", Menlo, Consolas, monospace;
                font-size: 12px;
            }
            QListWidget#filesList::item {
                padding: 5px 6px;
            }
            QListWidget#filesList::item:selected {
                color: #ffffff;
                background: #2f5f7f;
                border-radius: 4px;
            }
            QLabel#fieldLabel {
                color: #334e68;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
            }
            QLineEdit {
                min-height: 36px;
                padding: 0 12px;
                color: #1f2933;
                background: #ffffff;
                border: 1px solid #b8c7d4;
                border-radius: 6px;
                selection-background-color: #2f5f7f;
            }
            QLineEdit:focus {
                border: 1px solid #2f5f7f;
                background: #fbfdff;
            }
            QPushButton {
                min-height: 36px;
                padding: 0 16px;
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
                color: #ffffff;
                background: #2f5f7f;
                border-color: #274f6a;
            }
            QPushButton#primaryButton:hover {
                background: #274f6a;
            }
            QLabel#engineStatus {
                color: #19364d;
                font-weight: 800;
            }
            QLabel#runStatus {
                color: #52606d;
                font-weight: 700;
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
                padding: 12px;
                font-family: "SF Mono", Menlo, Consolas, monospace;
                font-size: 12px;
                selection-background-color: #2f5f7f;
            }
            QLabel#outputPath {
                color: #1f2933;
                font-family: "SF Mono", Menlo, Consolas, monospace;
                background: #f4f7fa;
                border: 1px solid #d5dee7;
                border-radius: 6px;
                padding: 8px 10px;
            }
            """
        )

    def generate(self):
        if self.worker is not None and self.worker.isRunning():
            return

        topic = self.topic.text().strip()

        if not topic:
            self.run_status.setText("Waiting for Topic")
            self.append_console("Warning: Topic is required before generation.")
            QMessageBox.warning(
                self,
                "Topic Required",
                "Please enter a topic before starting production.",
            )
            self.topic.setFocus()
            return

        self.console.clear()
        self.summary_panel.hide()
        self.files_panel.hide()
        self.production_result = None
        self.run_status.setText("Running")

        self.progress.show()
        self.set_controls_enabled(False)

        self.worker = ProductionWorker(topic)

        self.worker.log.connect(self.append_console)

        self.worker.finished.connect(self.finished)

        self.worker.start()

    def finished(self, result):
        self.progress.hide()

        self.set_controls_enabled(True)
        self.production_result = result

        if result.success:
            self.run_status.setText("Completed")
            self.update_summary(result)
            self.update_generated_files(result)
            self.append_console("")
            self.append_console("==========")
            self.append_console("Production Completed")
            self.open_output_folder()
            QMessageBox.information(
                self,
                "Production Completed",
                "Production completed successfully.",
            )
        else:
            self.run_status.setText("Failed")
            self.append_console("")
            self.append_console("==========")
            self.append_console("Production Failed")
            QMessageBox.critical(
                self,
                "Production Failed",
                "Production could not be completed. Please review the production log.",
            )

    def clear_console(self):
        self.console.clear()
        self.console.setText("Waiting for Topic...")
        self.run_status.setText("Waiting for Topic")
        self.summary_panel.hide()
        self.files_panel.hide()

    def append_console(self, text):
        self.console.append(text)
        self.console.moveCursor(QTextCursor.End)

    def set_controls_enabled(self, enabled):
        self.topic.setEnabled(enabled)
        self.btn.setEnabled(enabled)
        self.clear_btn.setEnabled(enabled)
        self.output_btn.setEnabled(enabled)
        self.files_list.setEnabled(enabled)

    def update_summary(self, result: ProductionResult):
        self.summary_topic.setText(self.topic.text().strip() or "—")
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

        if not result.generated_files:
            item = QListWidgetItem("No generated documents.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)
            self.files_list.addItem(item)
        else:
            for document in result.generated_files:
                item = QListWidgetItem(document.name)
                item.setData(Qt.UserRole, str(document))
                self.files_list.addItem(item)

        self.files_panel.show()

    def open_generated_file(self, item):
        path = item.data(Qt.UserRole)

        if not path:
            return

        document = Path(path)

        if not document.exists():
            return

        system = platform.system()

        if system == "Darwin":
            subprocess.Popen(["open", str(document)])
        elif system == "Windows":
            os.startfile(str(document))
        else:
            subprocess.Popen(["xdg-open", str(document)])

    def open_output_folder(self):
        if self.production_result is None:
            return

        output = self.production_result.output_dir

        if output is None or not output.exists():
            return

        system = platform.system()

        if system == "Darwin":
            subprocess.Popen(["open", str(output)])
        elif system == "Windows":
            os.startfile(str(output))
        else:
            subprocess.Popen(["xdg-open", str(output)])
