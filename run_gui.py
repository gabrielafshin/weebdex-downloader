#!/usr/bin/env python3
"""
Weebdex Downloader GUI - PyQt6 Interface

Usage:
    python run_gui.py

A modern graphical interface for downloading manga from weebdex.org.
"""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow
from gui.styles import apply_theme
from src.config import get_config
from src.utils.logging import setup_logging


def main():
    """Launch the GUI application."""
    # Load config
    config = get_config()
    
    # Setup logging
    setup_logging(enabled=config.enable_logs)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Weebdex Downloader")
    app.setApplicationVersion("1.0.0")
    
    # Apply dark theme
    apply_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
