from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSplashScreen
from PySide6.QtGui import QPixmap


class LucidSplash(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(700, 400)
        pixmap.fill(Qt.white)

        super().__init__(pixmap)

        self.showMessage(
            "\n\n🚀 LUCID AUTO\n\nHGPT STEEL\n\nLoading...",
            Qt.AlignCenter,
            Qt.black,
        )