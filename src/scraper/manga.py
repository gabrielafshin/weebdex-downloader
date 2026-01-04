"""Manga scraper for weebdex.org."""

import re
import logging
from typing import Optional, List, Tuple

from ..api.client import WeebdexClient, APIError
from ..models import MangaInfo, Chapter, ChapterImages


logger = logging.getLogger(__name__)


class MangaScraper:
    """High-level scraper for manga information and chapters."""
    
    # Pattern to extract manga ID from URL
    URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?weebdex\.org/title/([a-zA-Z0-9]+)"
    )
    
    def __init__(self):
        """Initialize scraper with API client."""
        self.client = WeebdexClient()
    
    def close(self) -> None:
        """Close the underlying client."""
        self.client.close()
    
    def __enter__(self) -> "MangaScraper":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
    
    @classmethod
    def extract_manga_id(cls, url: str) -> Optional[str]:
        """
        Extract manga ID from weebdex.org URL.
        
        Supports:
        - https://weebdex.org/title/k4ak071n49
        - https://weebdex.org/title/k4ak071n49/manga-name
        - weebdex.org/title/k4ak071n49
        
        Returns None if URL is invalid.
        """
        match = cls.URL_PATTERN.search(url)
        if match:
            return match.group(1)
        return None
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Check if URL is a valid weebdex.org manga URL."""
        return cls.extract_manga_id(url) is not None
    
    def fetch_manga_details(self, manga_id: str) -> MangaInfo:
        """
        Fetch complete manga information.
        
        Args:
            manga_id: The manga ID to fetch
            
        Returns:
            MangaInfo object with all details
            
        Raises:
            APIError: If the API request fails
        """
        logger.info(f"Fetching manga info for: {manga_id}")
        return self.client.get_manga_info(manga_id)
    
    def fetch_chapter_list(self, manga_id: str) -> List[Chapter]:
        """
        Fetch all chapters for a manga.
        
        Args:
            manga_id: The manga ID to fetch chapters for
            
        Returns:
            List of Chapter objects sorted by chapter number (ascending)
            
        Raises:
            APIError: If the API request fails
        """
        logger.info(f"Fetching chapters for: {manga_id}")
        return self.client.get_chapters(manga_id)
    
    def fetch_chapter_images(self, chapter_id: str) -> ChapterImages:
        """
        Fetch image data for a chapter.
        
        Args:
            chapter_id: The chapter ID to fetch images for
            
        Returns:
            ChapterImages object with image URLs
            
        Raises:
            APIError: If the API request fails
        """
        logger.debug(f"Fetching images for chapter: {chapter_id}")
        return self.client.get_chapter_images(chapter_id)
    
    def fetch_manga_with_chapters(
        self,
        url_or_id: str
    ) -> Tuple[MangaInfo, List[Chapter]]:
        """
        Convenience method to fetch both manga info and chapters.
        
        Args:
            url_or_id: Either a weebdex.org URL or manga ID
            
        Returns:
            Tuple of (MangaInfo, List[Chapter])
            
        Raises:
            ValueError: If URL is invalid
            APIError: If the API request fails
        """
        # Try to extract ID from URL first
        manga_id = self.extract_manga_id(url_or_id)
        if manga_id is None:
            # Assume it's already an ID
            manga_id = url_or_id
        
        manga_info = self.fetch_manga_details(manga_id)
        chapters = self.fetch_chapter_list(manga_id)
        
        return manga_info, chapters
