"""Manga information card widget."""

from typing import Optional
import io

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QSizePolicy, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

import httpx

from src.models import MangaInfo


class MangaCard(QFrame):
    """Widget displaying manga information with cover image."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the card layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Cover image
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(180, 260)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a4a;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.cover_label)
        
        # Info section
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.title_label.setWordWrap(True)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout.addWidget(self.title_label)
        
        # Alt title
        self.alt_title_label = QLabel()
        self.alt_title_label.setObjectName("subtitle")
        self.alt_title_label.setWordWrap(True)
        info_layout.addWidget(self.alt_title_label)
        
        # Spacer
        info_layout.addSpacing(8)
        
        # Metadata grid
        self.status_label = self._create_info_label("Status:")
        self.year_label = self._create_info_label("Year:")
        self.author_label = self._create_info_label("Author:")
        self.artist_label = self._create_info_label("Artist:")
        self.genres_label = self._create_info_label("Genres:")
        
        info_layout.addWidget(self.status_label)
        info_layout.addWidget(self.year_label)
        info_layout.addWidget(self.author_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.genres_label)
        
        info_layout.addStretch()
        
        # Description
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #a0a0a0; font-size: 13px;")
        self.desc_label.setMaximumHeight(80)
        info_layout.addWidget(self.desc_label)
        
        layout.addWidget(info_widget, 1)
    
    def _create_info_label(self, prefix: str) -> QLabel:
        """Create a label for info display."""
        label = QLabel()
        label.setStyleSheet("font-size: 14px;")
        return label
    
    def set_manga(self, manga: MangaInfo):
        """Update the card with manga information."""
        # Title
        self.title_label.setText(manga.title)
        
        # Alt title
        alt_titles = manga.alt_titles.get("en", [])
        if alt_titles:
            self.alt_title_label.setText(alt_titles[0])
            self.alt_title_label.show()
        else:
            self.alt_title_label.hide()
        
        # Metadata
        status_color = "#4ade80" if manga.status == "ongoing" else "#ef4444"
        self.status_label.setText(
            f"<b>Status:</b> <span style='color:{status_color}'>{manga.status.title()}</span>"
        )
        self.year_label.setText(f"<b>Year:</b> {manga.year}")
        
        authors = ", ".join(a.name for a in manga.authors) or "Unknown"
        self.author_label.setText(f"<b>Author:</b> {authors}")
        
        artists = ", ".join(a.name for a in manga.artists) or "Unknown"
        self.artist_label.setText(f"<b>Artist:</b> {artists}")
        
        genres = ", ".join(manga.get_genres()) or "N/A"
        self.genres_label.setText(f"<b>Genres:</b> {genres}")
        
        # Description
        desc = manga.description or "No description available."
        if len(desc) > 300:
            desc = desc[:300] + "..."
        self.desc_label.setText(desc)
        
        # Load cover image
        if manga.cover:
            self._load_cover(manga.cover.get_url(manga.id))
    
    def _load_cover(self, url: str):
        """Load cover image from URL."""
        try:
            headers = {
                "User-Agent": "WeebdexDownloader/1.0",
                "Referer": "https://weebdex.org/",
                "Accept": "image/*,*/*",
            }
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    # Scale to fit
                    scaled = pixmap.scaled(
                        180, 260,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.cover_label.setPixmap(scaled)
                else:
                    self.cover_label.setText("Cover\nUnavailable")
        except Exception as e:
            self.cover_label.setText("Cover\nUnavailable")
    
    def clear(self):
        """Clear the card content."""
        self.title_label.clear()
        self.alt_title_label.clear()
        self.status_label.clear()
        self.year_label.clear()
        self.author_label.clear()
        self.artist_label.clear()
        self.genres_label.clear()
        self.desc_label.clear()
        self.cover_label.clear()
        self.cover_label.setText("")
