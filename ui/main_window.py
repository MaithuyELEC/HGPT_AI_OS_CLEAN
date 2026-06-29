"""LUCID Main Window - PySide6 Qt Application."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon


class MainWindow(QMainWindow):
    """Main application window for LUCID AI Engineering Platform."""

    def __init__(self):
        """Initialize main window with layout and styling."""
        super().__init__()
        self.setWindowTitle("LUCID - AI Engineering Platform")
        self.setGeometry(100, 100, 1600, 900)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content area (Sidebar + Center)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Center content
        center = self._create_center()
        content_layout.addWidget(center, 1)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        # Footer
        footer = self._create_footer()
        main_layout.addWidget(footer)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Apply styling
        self._apply_styling()

    def _create_header(self) -> QFrame:
        """Create header section."""
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a1a; border-bottom: 2px solid #00d4ff;")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("LUCID")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("AI Engineering Platform")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # Developer
        dev_label = QLabel("Developed by MaithuyELEC")
        dev_font = QFont()
        dev_font.setPointSize(10)
        dev_label.setFont(dev_font)
        dev_label.setStyleSheet("color: #808080;")
        layout.addWidget(dev_label)
        
        header.setLayout(layout)
        return header

    def _create_sidebar(self) -> QFrame:
        """Create left sidebar with navigation buttons."""
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #0f0f0f; border-right: 1px solid #333333;")
        sidebar.setFixedWidth(220)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(8)
        
        # Navigation buttons
        buttons = [
            ("🏠", "Dashboard"),
            ("📝", "Marketing"),
            ("🎬", "Video Studio"),
            ("🖼", "Image Studio"),
            ("📚", "Knowledge Base"),
            ("📄", "SOP Generator"),
            ("✅", "QA/QC"),
            ("🔧", "Maintenance"),
            ("📊", "Planner"),
            ("⚙", "Settings"),
        ]
        
        for icon, text in buttons:
            btn = self._create_nav_button(f"{icon}  {text}")
            layout.addWidget(btn)
        
        layout.addStretch()
        sidebar.setLayout(layout)
        return sidebar

    def _create_nav_button(self, text: str) -> QPushButton:
        """Create a styled navigation button."""
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                color: #00d4ff;
                border-left: 3px solid #00d4ff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
                border-left: 3px solid #00d4ff;
            }
        """)
        return btn

    def _create_center(self) -> QFrame:
        """Create center dashboard area."""
        center = QFrame()
        center.setStyleSheet("background-color: #1a1a1a;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Welcome title
        welcome_label = QLabel("Welcome to LUCID")
        welcome_font = QFont()
        welcome_font.setPointSize(28)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #00d4ff;")
        layout.addWidget(welcome_label)
        
        # Subtitle
        subtitle_label = QLabel("AI Engineering Platform")
        subtitle_font = QFont()
        subtitle_font.setPointSize(16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        center.setLayout(layout)
        return center

    def _create_footer(self) -> QFrame:
        """Create footer section."""
        footer = QFrame()
        footer.setStyleSheet("background-color: #0f0f0f; border-top: 1px solid #333333;")
        footer.setFixedHeight(40)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(20)
        
        # Status
        status_label = QLabel("Status : Ready")
        status_label.setStyleSheet("color: #00d4ff; font-weight: bold;")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        # Version
        version_label = QLabel("Version 3.0")
        version_label.setStyleSheet("color: #808080; font-size: 10px;")
        layout.addWidget(version_label)
        
        footer.setLayout(layout)
        return footer

    def _apply_styling(self):
        """Apply global application styling."""
        dark_stylesheet = """
            QMainWindow {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #e0e0e0;
            }
            QScrollBar:vertical {
                background-color: #0f0f0f;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00d4ff;
            }
            QScrollBar:horizontal {
                background-color: #0f0f0f;
                height: 12px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background-color: #333333;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #00d4ff;
            }
        """
        self.setStyleSheet(dark_stylesheet)
