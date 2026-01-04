"""Utility module for Weebdex Downloader."""

from .logging import setup_logging
from .comicinfo import generate_comicinfo_xml

__all__ = ["setup_logging", "generate_comicinfo_xml"]
