"""API client for weebdex.org with retry logic."""

import time
import logging
from typing import Dict, Any, Optional, List

import httpx

from ..models import MangaInfo, Chapter, ChapterImages


logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""
    pass


class WeebdexClient:
    """HTTP client for weebdex.org API with retry logic."""
    
    BASE_URL = "https://api.weebdex.org"
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_DELAYS = [2, 4, 6]  # Seconds between retries
    
    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """Initialize the client."""
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers={
                    "User-Agent": "WeebdexDownloader/1.0",
                    "Accept": "application/json",
                }
            )
        return self._client
    
    def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            self._client.close()
    
    def __enter__(self) -> "WeebdexClient":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
    
    def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        last_error: Optional[Exception] = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Request attempt {attempt + 1}: {method} {url}")
                response = self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"HTTP error {e.response.status_code}: {e}")
                
                # Don't retry on client errors (4xx) except 429 (rate limit)
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    raise APIError(f"API error: {e.response.status_code}") from e
                    
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Request error: {e}")
            
            # Wait before retry
            if attempt < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAYS[attempt]
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        raise APIError(f"Failed after {self.MAX_RETRIES} attempts: {last_error}")
    
    def get_manga_info(self, manga_id: str) -> MangaInfo:
        """Fetch manga information by ID."""
        url = f"{self.BASE_URL}/manga/{manga_id}"
        data = self._request_with_retry("GET", url)
        return MangaInfo.from_api_response(data)
    
    def get_chapters(
        self,
        manga_id: str,
        limit: int = 500,
        order: str = "desc"
    ) -> List[Chapter]:
        """Fetch chapter list for a manga."""
        url = f"{self.BASE_URL}/manga/{manga_id}/chapters"
        params = {"limit": limit, "order": order}
        data = self._request_with_retry("GET", url, params=params)
        
        chapters = [
            Chapter.from_api_response(ch)
            for ch in data.get("data", [])
        ]
        
        # Sort by chapter number (ascending for display)
        chapters.sort(key=lambda c: c.get_chapter_number())
        return chapters
    
    def get_chapter_images(self, chapter_id: str) -> ChapterImages:
        """Fetch chapter image data."""
        url = f"{self.BASE_URL}/chapter/{chapter_id}"
        data = self._request_with_retry("GET", url)
        return ChapterImages.from_api_response(data)
