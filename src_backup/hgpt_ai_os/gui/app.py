import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from hgpt_ai_os.gui.main_window import MainWindow
from hgpt_ai_os.gui.splash import LucidSplash


def main():
    app = QApplication(sys.argv)

    splash = LucidSplash()
    splash.show()

    app.processEvents()

    window = None

    def start():
        nonlocal window

        window = MainWindow()
        window.show()

        splash.finish(window)

    QTimer.singleShot(2000, start)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()