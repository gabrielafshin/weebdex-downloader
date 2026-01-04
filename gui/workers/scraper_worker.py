"""Background worker for scraping manga info and chapters."""

from PyQt6.QtCore import QThread, pyqtSignal

from src.scraper.manga import MangaScraper
from src.models import MangaInfo, Chapter
from src.api.client import APIError


class ScraperWorker(QThread):
    """Worker thread for fetching manga information."""
    
    # Signals
    finished = pyqtSignal(object, list)  # manga_info, chapters
    error = pyqtSignal(str)
    
    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
    
    def run(self):
        """Fetch manga info and chapters in background."""
        try:
            with MangaScraper() as scraper:
                # Validate URL first
                manga_id = scraper.extract_manga_id(self.url)
                if not manga_id:
                    self.error.emit("Invalid weebdex.org URL")
                    return
                
                # Fetch manga info and chapters
                manga_info, chapters = scraper.fetch_manga_with_chapters(self.url)
                
                if not chapters:
                    self.error.emit("No chapters found for this manga")
                    return
                
                self.finished.emit(manga_info, chapters)
                
        except APIError as e:
            self.error.emit(f"API Error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
