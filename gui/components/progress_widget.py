"""Progress widget for download status display."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import pyqtSignal


class ProgressWidget(QFrame):
    """Widget for displaying download progress."""
    
    cancel_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Setup the widget layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        self.title_label = QLabel("Downloading...")
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status row
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        
        self.status_label = QLabel("Preparing...")
        self.status_label.setStyleSheet("color: #a0a0a0;")
        status_row.addWidget(self.status_label, 1)
        
        self.count_label = QLabel("0/0")
        self.count_label.setStyleSheet("font-weight: bold;")
        status_row.addWidget(self.count_label)
        
        layout.addLayout(status_row)
        
        # Cancel button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        btn_row.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_row)
    
    def start(self, total: int):
        """Start progress display."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        self.title_label.setText("Downloading...")
        self.status_label.setText("Starting...")
        self.count_label.setText(f"0/{total}")
        self.cancel_btn.setEnabled(True)
        self.show()
    
    def update_progress(self, current: int, total: int, message: str):
        """Update progress display."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(message)
        self.count_label.setText(f"{current}/{total}")
    
    def finish(self, successful: int, failed: int):
        """Show completion status."""
        total = successful + failed
        
        if failed == 0:
            self.title_label.setText("✓ Download Complete!")
            self.title_label.setStyleSheet("color: #4ade80; font-size: 18px; font-weight: bold;")
            self.status_label.setText(f"Successfully downloaded {successful} chapter(s)")
        else:
            self.title_label.setText("⚠ Download Finished with Errors")
            self.title_label.setStyleSheet("color: #fbbf24; font-size: 18px; font-weight: bold;")
            self.status_label.setText(f"Downloaded {successful}/{total} chapters, {failed} failed")
        
        self.progress_bar.setValue(total)
        self.count_label.setText(f"{total}/{total}")
        self.cancel_btn.setText("Close")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.hide)
    
    def show_error(self, message: str):
        """Show error status."""
        self.title_label.setText("✗ Error")
        self.title_label.setStyleSheet("color: #ef4444; font-size: 18px; font-weight: bold;")
        self.status_label.setText(message)
        self.progress_bar.setValue(0)
        self.cancel_btn.setText("Close")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.hide)
    
    def reset(self):
        """Reset the widget for reuse."""
        self.title_label.setText("Downloading...")
        self.title_label.setStyleSheet("")
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing...")
        self.count_label.setText("0/0")
        self.cancel_btn.setText("Cancel")
        try:
            self.cancel_btn.clicked.disconnect()
        except TypeError:
            pass
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        self.cancel_btn.setEnabled(True)
        self.hide()
