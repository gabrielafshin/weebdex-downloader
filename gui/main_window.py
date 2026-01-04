"""Main application window with sidebar navigation."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QFrame, QLabel,
    QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from .screens.download_screen import DownloadScreen
from .screens.settings_screen import SettingsScreen
from .screens.about_screen import AboutScreen


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Weebdex Downloader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.stack = QStackedWidget()
        
        # Create screens
        self.download_screen = DownloadScreen()
        self.settings_screen = SettingsScreen()
        self.about_screen = AboutScreen()
        
        self.stack.addWidget(self.download_screen)
        self.stack.addWidget(self.settings_screen)
        self.stack.addWidget(self.about_screen)
        
        main_layout.addWidget(self.stack, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_sidebar(self) -> QFrame:
        """Create the sidebar with navigation buttons."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(8)
        
        # Logo
        logo = QLabel("📚 Weebdex")
        logo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #e94560;
            padding: 8px;
        """)
        layout.addWidget(logo)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = []
        
        download_btn = self._create_nav_button("📥  Download", 0)
        download_btn.setChecked(True)
        self.nav_buttons.append(download_btn)
        layout.addWidget(download_btn)
        
        settings_btn = self._create_nav_button("⚙️  Settings", 1)
        self.nav_buttons.append(settings_btn)
        layout.addWidget(settings_btn)
        
        about_btn = self._create_nav_button("ℹ️  About", 2)
        self.nav_buttons.append(about_btn)
        layout.addWidget(about_btn)
        
        layout.addStretch()
        
        # Version at bottom
        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #666; font-size: 12px; padding: 8px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        return sidebar
    
    def _create_nav_button(self, text: str, index: int) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self._navigate_to(index))
        return btn
    
    def _navigate_to(self, index: int):
        """Navigate to a screen by index."""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Switch screen
        self.stack.setCurrentIndex(index)
        
        # Update status bar
        screen_names = ["Download", "Settings", "About"]
        self.status_bar.showMessage(f"{screen_names[index]} screen")
