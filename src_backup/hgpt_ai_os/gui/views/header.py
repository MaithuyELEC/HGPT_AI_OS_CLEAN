from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget


class HeaderPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("🚀 LUCID AUTO")
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        version = QLabel("v1.1")
        version.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(version)