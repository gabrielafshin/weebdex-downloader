"""Image downloading with retry logic."""

import time
import logging
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx


logger = logging.getLogger(__name__)


class ImageDownloadError(Exception):
    """Custom exception for image download errors."""
    pass


class ImageDownloader:
    """Downloads images with retry logic and concurrent support."""
    
    DEFAULT_TIMEOUT = 60.0
    MAX_RETRIES = 3
    RETRY_DELAYS = [2, 4, 6]  # Exponential-ish backoff
    
    def __init__(self, max_workers: int = 5, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize image downloader.
        
        Args:
            max_workers: Maximum concurrent downloads
            timeout: Request timeout in seconds
        """
        self.max_workers = max_workers
        self.timeout = timeout
    
    def download_image(
        self,
        url: str,
        output_path: Path,
        referer: str = "https://weebdex.org/"
    ) -> bool:
        """
        Download a single image with retry logic.
        
        Args:
            url: Image URL to download
            output_path: Path to save the image
            referer: Referer header value
            
        Returns:
            True if download succeeded, False otherwise
        """
        headers = {
            "User-Agent": "WeebdexDownloader/1.0",
            "Referer": referer,
            "Accept": "image/*,*/*",
        }
        
        last_error: Optional[Exception] = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Downloading (attempt {attempt + 1}): {url}")
                
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    
                    # Ensure parent directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write image data
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    
                    logger.debug(f"Saved: {output_path}")
                    return True
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"HTTP error {e.response.status_code} for {url}")
                
                # Don't retry on 404
                if e.response.status_code == 404:
                    logger.error(f"Image not found: {url}")
                    return False
                    
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Request error for {url}: {e}")
            
            except IOError as e:
                last_error = e
                logger.error(f"IO error saving {output_path}: {e}")
                return False
            
            # Wait before retry
            if attempt < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAYS[attempt]
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        logger.error(f"Failed after {self.MAX_RETRIES} attempts: {url}")
        return False
    
    def download_images(
        self,
        images: List[Tuple[str, Path]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[int, int]:
        """
        Download multiple images concurrently.
        
        Args:
            images: List of (url, output_path) tuples
            progress_callback: Optional callback(completed, total, filename)
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        if not images:
            return 0, 0
        
        total = len(images)
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_image = {
                executor.submit(self.download_image, url, path): (url, path)
                for url, path in images
            }
            
            # Process completed downloads
            for future in as_completed(future_to_image):
                url, path = future_to_image[future]
                
                try:
                    if future.result():
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Unexpected error downloading {url}: {e}")
                    failed += 1
                
                # Report progress
                completed = successful + failed
                if progress_callback:
                    progress_callback(completed, total, path.name)
        
        return successful, failed
