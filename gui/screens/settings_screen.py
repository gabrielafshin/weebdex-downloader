"""Settings screen for application configuration."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QSpinBox, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt

from src.config import Config, get_config, save_config, DownloadFormat


class SettingsScreen(QWidget):
    """Settings configuration screen."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the screen layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Settings")
        header.setObjectName("title")
        layout.addWidget(header)
        
        subtitle = QLabel("Configure download preferences and application behavior")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)
        
        # Download settings group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)
        download_layout.setSpacing(16)
        download_layout.setContentsMargins(16, 24, 16, 16)
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItem("Images (save as image files)", "images")
        self.format_combo.addItem("PDF (combine into PDF)", "pdf")
        self.format_combo.addItem("CBZ (comic book archive)", "cbz")
        download_layout.addRow("Download Format:", self.format_combo)
        
        # Keep images
        self.keep_images_check = QCheckBox("Keep images after PDF/CBZ conversion")
        download_layout.addRow("", self.keep_images_check)
        
        # Download path
        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("./downloads")
        path_row.addWidget(self.path_input, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.clicked.connect(self._browse_path)
        path_row.addWidget(browse_btn)
        
        download_layout.addRow("Download Path:", path_row)
        
        layout.addWidget(download_group)
        
        # Concurrency settings group
        concurrency_group = QGroupBox("Concurrency Settings")
        concurrency_layout = QFormLayout(concurrency_group)
        concurrency_layout.setSpacing(16)
        concurrency_layout.setContentsMargins(16, 24, 16, 16)
        
        # Concurrent chapters
        self.chapters_spin = QSpinBox()
        self.chapters_spin.setRange(1, 10)
        self.chapters_spin.setToolTip("Number of chapters to download simultaneously")
        concurrency_layout.addRow("Concurrent Chapters:", self.chapters_spin)
        
        # Concurrent images
        self.images_spin = QSpinBox()
        self.images_spin.setRange(1, 20)
        self.images_spin.setToolTip("Number of images to download per chapter simultaneously")
        concurrency_layout.addRow("Concurrent Images:", self.images_spin)
        
        layout.addWidget(concurrency_group)
        
        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setSpacing(16)
        advanced_layout.setContentsMargins(16, 24, 16, 16)
        
        # Enable logs
        self.logs_check = QCheckBox("Enable detailed logs (for debugging)")
        advanced_layout.addRow("", self.logs_check)
        
        layout.addWidget(advanced_group)
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("secondaryBtn")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_row.addWidget(reset_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        btn_row.addWidget(save_btn)
        
        layout.addLayout(btn_row)
        layout.addStretch()
    
    def _load_settings(self):
        """Load current settings into UI."""
        config = get_config()
        
        # Format
        index = self.format_combo.findData(config.download_format)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
        
        # Keep images
        self.keep_images_check.setChecked(config.keep_images)
        
        # Path
        self.path_input.setText(config.download_path)
        
        # Concurrency
        self.chapters_spin.setValue(config.concurrent_chapters)
        self.images_spin.setValue(config.concurrent_images)
        
        # Logs
        self.logs_check.setChecked(config.enable_logs)
    
    def _save_settings(self):
        """Save settings from UI."""
        config = get_config()
        
        # Update config
        config.download_format = self.format_combo.currentData()
        config.keep_images = self.keep_images_check.isChecked()
        config.download_path = self.path_input.text() or "./downloads"
        config.concurrent_chapters = self.chapters_spin.value()
        config.concurrent_images = self.images_spin.value()
        config.enable_logs = self.logs_check.isChecked()
        
        # Save
        save_config(config)
        
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
    
    def _reset_defaults(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Create default config
            default = Config()
            save_config(default)
            self._load_settings()
            QMessageBox.information(self, "Settings", "Settings reset to defaults!")
    
    def _browse_path(self):
        """Open folder browser for download path."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            self.path_input.text() or "."
        )
        if path:
            self.path_input.setText(path)
