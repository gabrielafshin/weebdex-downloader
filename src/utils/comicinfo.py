"""ComicInfo.xml generator for CBZ archives."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Optional

from ..models import MangaInfo, Chapter


def generate_comicinfo_xml(
    manga_info: MangaInfo,
    chapter: Chapter
) -> str:
    """
    Generate ComicInfo.xml content for a CBZ archive.
    
    ComicInfo.xml is a metadata format used by comic readers like ComicRack.
    Reference: https://anansi-project.github.io/docs/comicinfo/documentation
    
    Args:
        manga_info: Manga information
        chapter: Chapter information
        
    Returns:
        XML string for ComicInfo.xml
    """
    root = ET.Element("ComicInfo")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    
    # Title (Chapter title)
    title = chapter.get_display_name()
    ET.SubElement(root, "Title").text = title
    
    # Series (Manga title)
    ET.SubElement(root, "Series").text = manga_info.title
    
    # Number (Chapter number)
    try:
        chapter_num = float(chapter.chapter)
        ET.SubElement(root, "Number").text = str(chapter_num)
    except ValueError:
        ET.SubElement(root, "Number").text = chapter.chapter
    
    # Volume
    if chapter.volume:
        try:
            vol_num = int(chapter.volume)
            ET.SubElement(root, "Volume").text = str(vol_num)
        except ValueError:
            ET.SubElement(root, "Volume").text = chapter.volume
    
    # Summary
    if manga_info.description:
        ET.SubElement(root, "Summary").text = manga_info.description
    
    # Year
    if manga_info.year:
        ET.SubElement(root, "Year").text = str(manga_info.year)
    
    # Writer (Author)
    authors = [a.name for a in manga_info.authors]
    if authors:
        ET.SubElement(root, "Writer").text = ", ".join(authors)
    
    # Penciller (Artist)
    artists = [a.name for a in manga_info.artists]
    if artists:
        ET.SubElement(root, "Penciller").text = ", ".join(artists)
    
    # Genre
    genres = manga_info.get_genres()
    if genres:
        ET.SubElement(root, "Genre").text = ", ".join(genres)
    
    # Tags (themes)
    themes = manga_info.get_themes()
    if themes:
        ET.SubElement(root, "Tags").text = ", ".join(themes)
    
    # Language ISO (2-letter code)
    lang_map = {
        "en": "en",
        "ja": "ja",
        "ko": "ko",
        "zh": "zh",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt",
        "ru": "ru",
    }
    lang_iso = lang_map.get(chapter.language, chapter.language)
    if lang_iso:
        ET.SubElement(root, "LanguageISO").text = lang_iso
    
    # Manga format (Yes and reading direction)
    ET.SubElement(root, "Manga").text = "YesAndRightToLeft"
    
    # Age rating
    rating_map = {
        "safe": "Everyone",
        "suggestive": "Teen",
        "erotica": "Mature 17+",
        "pornographic": "Adults Only 18+"
    }
    age_rating = rating_map.get(manga_info.content_rating, "Unknown")
    ET.SubElement(root, "AgeRating").text = age_rating
    
    # Scanlation groups
    if chapter.groups:
        groups = [g.name for g in chapter.groups]
        ET.SubElement(root, "ScanInformation").text = ", ".join(groups)
    
    # Web link
    web_url = f"https://weebdex.org/title/{manga_info.id}"
    ET.SubElement(root, "Web").text = web_url
    
    # Format as pretty XML
    rough_string = ET.tostring(root, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding=None)
