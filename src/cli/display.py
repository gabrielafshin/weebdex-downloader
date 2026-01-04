"""Rich console display utilities for Weebdex Downloader."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from rich import box

from ..models import MangaInfo, Chapter
from ..config import Config, DownloadFormat


console = Console()


# ASCII art banner
BANNER = """
╦ ╦┌─┐┌─┐┌┐ ┌┬┐┌─┐─┐ ┬  ╔╦╗┌─┐┬ ┬┌┐┌┬  ┌─┐┌─┐┌┬┐┌─┐┬─┐
║║║├┤ ├┤ ├┴┐ ││├┤ ┌┴┬┘   ║║│ │││││││││  │ │├─┤ ││├┤ ├┬┘
╚╩╝└─┘└─┘└─┘─┴┘└─┘┴ └─  ═╩╝└─┘└┴┘┘└┘┴─┘└─┘┴ ┴─┴┘└─┘┴└─
"""


def show_banner() -> None:
    """Display the application banner."""
    console.print(
        Panel(
            Text(BANNER, style="bold cyan", justify="center"),
            border_style="cyan",
            padding=(0, 2)
        )
    )
    console.print(
        Text("  A Modern CLI for Downloading Manga from weebdex.org", 
             style="dim", justify="center")
    )
    console.print()


def show_manga_info(manga: MangaInfo) -> None:
    """Display manga information in a formatted panel."""
    # Build info text
    lines = []
    
    # Title
    lines.append(f"[bold cyan]{manga.title}[/bold cyan]")
    lines.append("")
    
    # Alternative titles
    if manga.alt_titles:
        for lang, titles in manga.alt_titles.items():
            if titles:
                lines.append(f"[dim]{lang.upper()}:[/dim] {titles[0]}")
        lines.append("")
    
    # Basic info
    info_items = []
    if manga.year:
        info_items.append(f"[yellow]Year:[/yellow] {manga.year}")
    if manga.status:
        status_color = "green" if manga.status == "ongoing" else "red"
        info_items.append(f"[yellow]Status:[/yellow] [{status_color}]{manga.status.title()}[/{status_color}]")
    if manga.demographic:
        info_items.append(f"[yellow]Demographic:[/yellow] {manga.demographic.title()}")
    if manga.content_rating:
        info_items.append(f"[yellow]Rating:[/yellow] {manga.content_rating.title()}")
    
    if info_items:
        lines.append(" | ".join(info_items))
        lines.append("")
    
    # Authors/Artists
    if manga.authors:
        author_names = ", ".join(a.name for a in manga.authors)
        lines.append(f"[yellow]Author:[/yellow] {author_names}")
    if manga.artists:
        artist_names = ", ".join(a.name for a in manga.artists)
        lines.append(f"[yellow]Artist:[/yellow] {artist_names}")
    
    # Genres
    genres = manga.get_genres()
    if genres:
        lines.append(f"[yellow]Genres:[/yellow] {', '.join(genres)}")
    
    # Themes
    themes = manga.get_themes()
    if themes:
        lines.append(f"[yellow]Themes:[/yellow] {', '.join(themes)}")
    
    lines.append("")
    
    # Description
    if manga.description:
        # Truncate long descriptions
        desc = manga.description
        if len(desc) > 500:
            desc = desc[:500] + "..."
        lines.append(f"[dim]{desc}[/dim]")
    
    console.print(Panel(
        "\n".join(lines),
        title="[bold]Manga Information[/bold]",
        border_style="blue",
        padding=(1, 2)
    ))


def show_chapters_table(
    chapters: List[Chapter],
    limit: int = 0
) -> None:
    """Display chapters in a formatted table."""
    table = Table(
        title="[bold]Available Chapters[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("#", style="dim", width=4)
    table.add_column("Chapter", style="cyan")
    table.add_column("Volume", style="yellow")
    table.add_column("Group", style="green")
    table.add_column("Language", style="blue", width=4)
    
    # Apply limit if set
    display_chapters = chapters
    truncated = False
    if limit > 0 and len(chapters) > limit:
        display_chapters = chapters[:limit]
        truncated = True
    
    for i, ch in enumerate(display_chapters, 1):
        group_name = ch.groups[0].name if ch.groups else "Unknown"
        table.add_row(
            str(i),
            f"Ch. {ch.chapter}",
            ch.volume or "-",
            group_name,
            ch.language.upper()
        )
    
    console.print(table)
    
    if truncated:
        remaining = len(chapters) - limit
        console.print(
            f"[dim]... and {remaining} more chapters. "
            f"Increase 'Max Chapters Display' in settings to show more.[/dim]"
        )
    
    console.print(f"\n[dim]Total: {len(chapters)} chapters[/dim]")


def show_settings(config: Config) -> None:
    """Display current settings."""
    table = Table(
        title="[bold]Current Settings[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Setting", style="yellow")
    table.add_column("Value", style="green")
    
    format_display = config.download_format.upper()
    table.add_row("Download Format", format_display)
    table.add_row("Keep Images (after conversion)", "Yes" if config.keep_images else "No")
    table.add_row("Concurrent Chapters", str(config.concurrent_chapters))
    table.add_row("Concurrent Images", str(config.concurrent_images))
    
    display_limit = "All" if config.max_chapters_display == 0 else str(config.max_chapters_display)
    table.add_row("Max Chapters Display", display_limit)
    
    table.add_row("Enable Detailed Logs", "Yes" if config.enable_logs else "No")
    table.add_row("Download Path", config.download_path)
    
    console.print(table)


def create_progress() -> Progress:
    """Create a Rich progress bar for downloads."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False
    )


def show_success(message: str) -> None:
    """Display a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def show_error(message: str) -> None:
    """Display an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def show_warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def show_info(message: str) -> None:
    """Display an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")
