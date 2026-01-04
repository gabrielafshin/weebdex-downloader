"""Configuration management for Weebdex Downloader."""

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class DownloadFormat(str, Enum):
    """Supported download formats."""
    IMAGES = "images"
    PDF = "pdf"
    CBZ = "cbz"


CONFIG_FILE = Path("config.json")


@dataclass
class Config:
    """Application configuration with defaults."""
    download_format: str = DownloadFormat.IMAGES.value
    keep_images: bool = True
    concurrent_chapters: int = 3
    concurrent_images: int = 5
    max_chapters_display: int = 0  # 0 = All
    enable_logs: bool = False
    download_path: str = "./downloads"
    
    def save(self) -> None:
        """Save configuration to JSON file."""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from JSON file or create default."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                return cls()
        return cls()
    
    def get_download_path(self) -> Path:
        """Get download path as Path object."""
        return Path(self.download_path)
    
    def get_format(self) -> DownloadFormat:
        """Get download format as enum."""
        return DownloadFormat(self.download_format)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def save_config(config: Config) -> None:
    """Save config and update global instance."""
    global _config
    config.save()
    _config = config
