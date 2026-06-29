from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class InputPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.topic = QLineEdit()
        self.topic.setPlaceholderText("Nhập chủ đề...")

        self.generate_btn = QPushButton("🚀 Generate")

        layout.addWidget(self.topic)
        layout.addWidget(self.generate_btn)