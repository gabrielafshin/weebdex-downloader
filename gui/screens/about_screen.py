"""About screen with application information."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt


class AboutScreen(QWidget):
    """About screen with app info and features."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the screen layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Logo/Title
        logo = QLabel("📚 Weebdex Downloader")
        logo.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #e94560;
        """)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("font-size: 16px; color: #a0a0a0;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(20)
        
        # Description card
        desc_card = QFrame()
        desc_card.setObjectName("card")
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(20, 20, 20, 20)
        desc_layout.setSpacing(12)
        
        desc_title = QLabel("About")
        desc_title.setObjectName("sectionTitle")
        desc_layout.addWidget(desc_title)
        
        desc_text = QLabel(
            "A modern manga downloader for weebdex.org with a beautiful interface.\n\n"
            "Download manga chapters in various formats with concurrent downloading\n"
            "support and comprehensive metadata generation."
        )
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("line-height: 1.5;")
        desc_layout.addWidget(desc_text)
        
        layout.addWidget(desc_card)
        
        # Features card
        features_card = QFrame()
        features_card.setObjectName("card")
        features_layout = QVBoxLayout(features_card)
        features_layout.setContentsMargins(20, 20, 20, 20)
        features_layout.setSpacing(12)
        
        features_title = QLabel("Features")
        features_title.setObjectName("sectionTitle")
        features_layout.addWidget(features_title)
        
        features = [
            "🚀 Concurrent chapter and image downloads",
            "📁 Multiple formats: Images, PDF, CBZ",
            "📋 ComicInfo.xml metadata for CBZ files",
            "🔄 Automatic retry with exponential backoff",
            "⚙️ Configurable concurrency settings",
            "🎨 Modern dark theme interface",
            "💾 Persistent configuration",
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setStyleSheet("font-size: 14px; padding: 4px 0;")
            features_layout.addWidget(label)
        
        layout.addWidget(features_card)
        
        # Links card
        links_card = QFrame()
        links_card.setObjectName("card")
        links_layout = QVBoxLayout(links_card)
        links_layout.setContentsMargins(20, 20, 20, 20)
        links_layout.setSpacing(12)
        
        links_title = QLabel("Links")
        links_title.setObjectName("sectionTitle")
        links_layout.addWidget(links_title)
        
        weebdex_link = QLabel(
            '<a href="https://weebdex.org" style="color: #e94560;">🌐 weebdex.org</a>'
        )
        weebdex_link.setOpenExternalLinks(True)
        weebdex_link.setStyleSheet("font-size: 14px;")
        links_layout.addWidget(weebdex_link)
        
        layout.addWidget(links_card)
        
        layout.addStretch()
