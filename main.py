#!/usr/bin/env python3
"""
Weebdex Downloader - A Modern CLI for Downloading Manga from weebdex.org

Usage:
    python main.py

Features:
    - Interactive menu with beautiful Rich UI
    - Concurrent chapter and image downloads using threading
    - Support for PDF, CBZ, and Images output formats
    - Retry logic with exponential backoff
    - ComicInfo.xml metadata for CBZ files
    - Persistent configuration

Author: Weebdex Downloader
Version: 1.0.0
"""

from src.cli import main


if __name__ == "__main__":
    main()
