"""Background worker for downloading chapters."""

from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt6.QtCore import QThread, pyqtSignal

from src.models import MangaInfo, Chapter
from src.config import Config
from src.downloader.chapter import ChapterDownloader


class DownloadWorker(QThread):
    """Worker thread for downloading chapters."""
    
    # Signals
    progress = pyqtSignal(int, int, str)  # current, total, message
    chapter_complete = pyqtSignal(str, bool)  # chapter_name, success
    finished = pyqtSignal(int, int)  # successful, failed
    error = pyqtSignal(str)
    
    def __init__(
        self,
        manga_info: MangaInfo,
        chapters: List[Chapter],
        config: Config,
        parent=None
    ):
        super().__init__(parent)
        self.manga_info = manga_info
        self.chapters = chapters
        self.config = config
        self._cancelled = False
    
    def cancel(self):
        """Request cancellation of the download."""
        self._cancelled = True
    
    def run(self):
        """Download chapters in background with concurrent execution."""
        try:
            total = len(self.chapters)
            successful = 0
            failed = 0
            
            with ChapterDownloader(self.config) as downloader:
                # Use ThreadPoolExecutor for concurrent chapter downloads
                with ThreadPoolExecutor(max_workers=self.config.concurrent_chapters) as executor:
                    # Submit all chapter downloads
                    future_to_chapter = {
                        executor.submit(
                            downloader.download_single_chapter,
                            self.manga_info,
                            chapter,
                            None
                        ): chapter
                        for chapter in self.chapters
                    }
                    
                    # Process completed downloads
                    for future in as_completed(future_to_chapter):
                        if self._cancelled:
                            executor.shutdown(wait=False, cancel_futures=True)
                            self.error.emit("Download cancelled")
                            return
                        
                        chapter = future_to_chapter[future]
                        chapter_name = chapter.get_display_name()
                        
                        try:
                            success, message = future.result()
                            if success:
                                successful += 1
                                self.chapter_complete.emit(chapter_name, True)
                            else:
                                failed += 1
                                self.chapter_complete.emit(chapter_name, False)
                        except Exception as e:
                            failed += 1
                            self.chapter_complete.emit(chapter_name, False)
                        
                        # Emit progress
                        completed = successful + failed
                        self.progress.emit(
                            completed,
                            total,
                            f"Downloaded {chapter_name}"
                        )
            
            self.finished.emit(successful, failed)
            
        except Exception as e:
            self.error.emit(f"Download error: {str(e)}")
