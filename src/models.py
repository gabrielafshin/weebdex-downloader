"""Data models for Weebdex Downloader."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Tag:
    """Manga tag model."""
    id: str
    group: str
    name: str


@dataclass
class Author:
    """Author/Artist model."""
    id: str
    name: str
    group: str = "author"


@dataclass
class Cover:
    """Cover image model."""
    id: str
    ext: str
    dimensions: List[int] = field(default_factory=list)
    
    def get_url(self, manga_id: str) -> str:
        """Get full cover URL."""
        return f"https://srv.notdelta.xyz/covers/{manga_id}/{self.id}{self.ext}"


@dataclass
class MangaInfo:
    """Complete manga information model."""
    id: str
    title: str
    description: str
    year: int
    language: str
    demographic: str
    status: str
    content_rating: str
    alt_titles: Dict[str, List[str]] = field(default_factory=dict)
    authors: List[Author] = field(default_factory=list)
    artists: List[Author] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)
    cover: Optional[Cover] = None
    available_languages: List[str] = field(default_factory=list)
    available_groups: List[Dict[str, str]] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "MangaInfo":
        """Create MangaInfo from API response."""
        relationships = data.get("relationships", {})
        
        # Parse authors
        authors = [
            Author(id=a["id"], name=a["name"], group=a.get("group", "author"))
            for a in relationships.get("authors", [])
        ]
        
        # Parse artists
        artists = [
            Author(id=a["id"], name=a["name"], group=a.get("group", "author"))
            for a in relationships.get("artists", [])
        ]
        
        # Parse tags
        tags = [
            Tag(id=t["id"], group=t["group"], name=t["name"])
            for t in relationships.get("tags", [])
        ]
        
        # Parse cover
        cover_data = relationships.get("cover")
        cover = Cover(
            id=cover_data["id"],
            ext=cover_data["ext"],
            dimensions=cover_data.get("dimensions", [])
        ) if cover_data else None
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            year=data.get("year", 0),
            language=data.get("language", ""),
            demographic=data.get("demographic", ""),
            status=data.get("status", ""),
            content_rating=data.get("content_rating", ""),
            alt_titles=data.get("alt_titles", {}),
            authors=authors,
            artists=artists,
            tags=tags,
            cover=cover,
            available_languages=relationships.get("available_languages", []),
            available_groups=relationships.get("available_groups", [])
        )
    
    def get_genres(self) -> List[str]:
        """Get list of genre names."""
        return [t.name for t in self.tags if t.group == "genre"]
    
    def get_themes(self) -> List[str]:
        """Get list of theme names."""
        return [t.name for t in self.tags if t.group == "theme"]


@dataclass
class ChapterGroup:
    """Scanlation group model."""
    id: str
    name: str


@dataclass
class Chapter:
    """Chapter model."""
    id: str
    volume: str
    chapter: str
    language: str
    version: int
    published_at: str
    groups: List[ChapterGroup] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Chapter":
        """Create Chapter from API response."""
        relationships = data.get("relationships", {})
        groups = [
            ChapterGroup(id=g["id"], name=g["name"])
            for g in relationships.get("groups", [])
        ]
        
        return cls(
            id=data["id"],
            volume=data.get("volume", ""),
            chapter=data.get("chapter", ""),
            language=data.get("language", "en"),
            version=data.get("version", 1),
            published_at=data.get("published_at", ""),
            groups=groups
        )
    
    def get_display_name(self) -> str:
        """Get formatted chapter name for display."""
        vol = f"Vol.{self.volume} " if self.volume else ""
        return f"{vol}Ch.{self.chapter}"
    
    def get_folder_name(self) -> str:
        """Get sanitized folder name for saving."""
        vol = f"Vol_{self.volume}_" if self.volume else ""
        # Handle decimal chapters properly
        ch_num = self.chapter.replace(".", "_")
        return f"{vol}Chapter_{ch_num}"
    
    def get_chapter_number(self) -> float:
        """Get chapter number as float for sorting."""
        try:
            return float(self.chapter)
        except ValueError:
            return 0.0


@dataclass
class ImageData:
    """Chapter image data model."""
    name: str
    dimensions: List[int] = field(default_factory=list)
    
    def get_url(self, node: str, chapter_id: str, optimized: bool = False) -> str:
        """Get full image URL."""
        quality = "optimized" if optimized else "data"
        return f"{node}/{quality}/{chapter_id}/{self.name}"


@dataclass
class ChapterImages:
    """Chapter images response model."""
    id: str
    volume: str
    chapter: str
    language: str
    node: str
    images: List[ImageData] = field(default_factory=list)
    images_optimized: List[ImageData] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ChapterImages":
        """Create ChapterImages from API response."""
        images = [
            ImageData(name=img["name"], dimensions=img.get("dimensions", []))
            for img in data.get("data", [])
        ]
        
        images_optimized = [
            ImageData(name=img["name"], dimensions=img.get("dimensions", []))
            for img in data.get("data_optimized", [])
        ]
        
        return cls(
            id=data["id"],
            volume=data.get("volume", ""),
            chapter=data.get("chapter", ""),
            language=data.get("language", "en"),
            node=data.get("node", ""),
            images=images,
            images_optimized=images_optimized
        )
    
    def get_image_urls(self, optimized: bool = False) -> List[str]:
        """Get list of image URLs."""
        source = self.images_optimized if optimized else self.images
        quality = "optimized" if optimized else "data"
        return [f"{self.node}/{quality}/{self.id}/{img.name}" for img in source]
