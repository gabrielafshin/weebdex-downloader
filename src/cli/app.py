"""Main CLI application for Weebdex Downloader."""

import sys
from typing import Optional

from rich.live import Live

from ..config import Config, get_config, save_config
from ..scraper.manga import MangaScraper
from ..downloader.chapter import ChapterDownloader
from ..utils.logging import setup_logging
from ..api.client import APIError

from .display import (
    console,
    show_banner,
    show_manga_info,
    show_chapters_table,
    show_success,
    show_error,
    show_warning,
    show_info,
    create_progress,
)
from .prompts import (
    prompt_main_menu,
    prompt_url,
    prompt_chapter_selection,
    prompt_settings_menu,
)


class WeebdexCLI:
    """Main CLI application class."""
    
    def __init__(self):
        """Initialize CLI application."""
        self.config = get_config()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging based on settings."""
        setup_logging(enabled=self.config.enable_logs)
    
    def run(self) -> None:
        """Run the main CLI loop."""
        show_banner()
        
        try:
            while True:
                choice = prompt_main_menu()
                
                if choice == 1:
                    self._handle_download()
                elif choice == 2:
                    self._handle_settings()
                elif choice == 3:
                    self._handle_exit()
                    break
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(0)
    
    def _handle_download(self) -> None:
        """Handle the download manga flow."""
        # Get URL
        url = prompt_url()
        if not url:
            return
        
        # Validate URL
        manga_id = MangaScraper.extract_manga_id(url)
        if not manga_id:
            show_error("Invalid weebdex.org URL. Please use format: https://weebdex.org/title/<id>")
            return
        
        # Fetch manga info
        console.print("\n[dim]Fetching manga information...[/dim]")
        
        try:
            with MangaScraper() as scraper:
                manga_info, chapters = scraper.fetch_manga_with_chapters(url)
        except APIError as e:
            show_error(f"Failed to fetch manga: {e}")
            return
        except Exception as e:
            show_error(f"Unexpected error: {e}")
            return
        
        if not chapters:
            show_warning("No chapters found for this manga.")
            return
        
        # Display manga info
        console.print()
        show_manga_info(manga_info)
        
        # Display chapters
        console.print()
        show_chapters_table(chapters, limit=self.config.max_chapters_display)
        
        # Get chapter selection
        selected_chapters = prompt_chapter_selection(chapters)
        if not selected_chapters:
            return
        
        # Download chapters
        self._download_chapters(manga_info, selected_chapters)
    
    def _download_chapters(self, manga_info, chapters) -> None:
        """Download selected chapters with progress display."""
        total = len(chapters)
        
        console.print(f"\n[bold]Downloading {total} chapter(s)...[/bold]")
        console.print(f"[dim]Format: {self.config.download_format.upper()} | "
                     f"Concurrent: {self.config.concurrent_chapters} chapters[/dim]\n")
        
        # Create progress display
        progress = create_progress()
        
        with progress:
            # Add overall task
            overall_task = progress.add_task(
                "[cyan]Downloading chapters...",
                total=total
            )
            
            completed = 0
            successful = 0
            failed = 0
            
            def on_chapter_complete(name: str, done: int, total: int, success: bool):
                nonlocal completed, successful, failed
                completed = done
                if success:
                    successful += 1
                else:
                    failed += 1
                progress.update(overall_task, completed=done)
            
            # Download with progress callback
            with ChapterDownloader(self.config) as downloader:
                successful, failed = downloader.download_chapters(
                    manga_info,
                    chapters,
                    progress_callback=on_chapter_complete
                )
        
        # Show results
        console.print()
        if failed == 0:
            show_success(f"Successfully downloaded {successful} chapter(s)!")
        else:
            show_warning(f"Downloaded {successful}/{total} chapters. {failed} failed.")
        
        show_info(f"Saved to: {self.config.download_path}")
    
    def _handle_settings(self) -> None:
        """Handle the settings menu."""
        self.config = prompt_settings_menu(self.config)
        self._setup_logging()  # Refresh logging settings
    
    def _handle_exit(self) -> None:
        """Handle exit."""
        console.print("\n[cyan]Thanks for using Weebdex Downloader! Goodbye![/cyan]")


def main() -> None:
    """Entry point for the CLI application."""
    cli = WeebdexCLI()
    cli.run()


if __name__ == "__main__":
    main()
