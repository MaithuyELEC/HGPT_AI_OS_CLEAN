import sys

from PySide6.QtWidgets import QApplication

from hgpt_ai_os.gui.branding import APP_DISPLAY_NAME, APP_ORGANIZATION, app_icon
from hgpt_ai_os.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_DISPLAY_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setWindowIcon(app_icon())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
