"""Chapter downloading with concurrent support."""

import re
import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models import MangaInfo, Chapter, ChapterImages
from ..scraper.manga import MangaScraper
from ..config import Config, DownloadFormat
from .images import ImageDownloader
from .converter import FormatConverter


logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Remove or replace invalid filename characters."""
    # Replace invalid characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    # Limit length
    return sanitized[:200] if len(sanitized) > 200 else sanitized


class ChapterDownloader:
    """Downloads manga chapters with concurrent support."""
    
    def __init__(self, config: Config):
        """
        Initialize chapter downloader.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.scraper = MangaScraper()
        self.image_downloader = ImageDownloader(
            max_workers=config.concurrent_images
        )
    
    def close(self) -> None:
        """Clean up resources."""
        self.scraper.close()
    
    def __enter__(self) -> "ChapterDownloader":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
    
    def get_chapter_path(
        self,
        manga_info: MangaInfo,
        chapter: Chapter
    ) -> Path:
        """Get the output path for a chapter."""
        base_path = self.config.get_download_path()
        manga_folder = sanitize_filename(manga_info.title)
        chapter_folder = chapter.get_folder_name()
        return base_path / manga_folder / chapter_folder
    
    def download_single_chapter(
        self,
        manga_info: MangaInfo,
        chapter: Chapter,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Download a single chapter.
        
        Args:
            manga_info: Manga information
            chapter: Chapter to download
            progress_callback: Optional callback(status, completed, total)
            
        Returns:
            Tuple of (success, message)
        """
        chapter_name = chapter.get_display_name()
        logger.info(f"Downloading {chapter_name}")
        
        try:
            # Fetch chapter image data
            chapter_images = self.scraper.fetch_chapter_images(chapter.id)
            image_urls = chapter_images.get_image_urls(optimized=False)
            
            if not image_urls:
                return False, f"No images found for {chapter_name}"
            
            # Prepare output directory
            chapter_path = self.get_chapter_path(manga_info, chapter)
            chapter_path.mkdir(parents=True, exist_ok=True)
            
            # Prepare image download list
            images_to_download: List[Tuple[str, Path]] = []
            for i, url in enumerate(image_urls, 1):
                # Get extension from URL
                ext = Path(url).suffix or ".jpg"
                filename = f"{i:03d}{ext}"
                output_path = chapter_path / filename
                images_to_download.append((url, output_path))
            
            # Download images with progress
            def image_progress(completed: int, total: int, filename: str):
                if progress_callback:
                    progress_callback(f"{chapter_name}: {filename}", completed, total)
            
            successful, failed = self.image_downloader.download_images(
                images_to_download,
                progress_callback=image_progress
            )
            
            if failed > 0:
                logger.warning(f"{chapter_name}: {failed} images failed to download")
            
            # Convert format if needed
            download_format = self.config.get_format()
            output_file: Optional[Path] = None
            
            if download_format == DownloadFormat.PDF:
                output_file = chapter_path.parent / f"{chapter.get_folder_name()}.pdf"
                FormatConverter.create_pdf(chapter_path, output_file)
                logger.info(f"Created PDF: {output_file}")
                
            elif download_format == DownloadFormat.CBZ:
                output_file = chapter_path.parent / f"{chapter.get_folder_name()}.cbz"
                FormatConverter.create_cbz(chapter_path, output_file, manga_info, chapter)
                logger.info(f"Created CBZ: {output_file}")
            
            # Clean up images if not keeping them
            if download_format != DownloadFormat.IMAGES and not self.config.keep_images:
                try:
                    shutil.rmtree(chapter_path)
                    logger.debug(f"Removed images folder: {chapter_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove images folder: {e}")
            
            return True, f"Downloaded {chapter_name} ({successful}/{len(images_to_download)} images)"
            
        except Exception as e:
            logger.error(f"Error downloading {chapter_name}: {e}")
            return False, f"Failed to download {chapter_name}: {e}"
    
    def download_chapters(
        self,
        manga_info: MangaInfo,
        chapters: List[Chapter],
        progress_callback: Optional[Callable[[str, int, int, bool], None]] = None
    ) -> Tuple[int, int]:
        """
        Download multiple chapters concurrently.
        
        Args:
            manga_info: Manga information
            chapters: List of chapters to download
            progress_callback: Optional callback(chapter_name, completed, total, success)
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        if not chapters:
            return 0, 0
        
        total = len(chapters)
        successful = 0
        failed = 0
        
        # Use ThreadPoolExecutor for concurrent chapter downloads
        with ThreadPoolExecutor(max_workers=self.config.concurrent_chapters) as executor:
            # Submit all chapter downloads
            future_to_chapter = {
                executor.submit(
                    self.download_single_chapter,
                    manga_info,
                    chapter,
                    None  # Individual progress not tracked in concurrent mode
                ): chapter
                for chapter in chapters
            }
            
            # Process completed downloads
            for future in as_completed(future_to_chapter):
                chapter = future_to_chapter[future]
                chapter_name = chapter.get_display_name()
                
                try:
                    success, message = future.result()
                    if success:
                        successful += 1
                        logger.info(message)
                    else:
                        failed += 1
                        logger.error(message)
                except Exception as e:
                    failed += 1
                    logger.error(f"Unexpected error: {chapter_name}: {e}")
                    success = False
                
                # Report progress
                completed = successful + failed
                if progress_callback:
                    progress_callback(chapter_name, completed, total, success)
        
        return successful, failed
