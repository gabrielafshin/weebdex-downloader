"""Format conversion utilities for PDF and CBZ."""

import io
import zipfile
import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image

from ..models import MangaInfo, Chapter
from ..utils.comicinfo import generate_comicinfo_xml


logger = logging.getLogger(__name__)


class FormatConverter:
    """Converts downloaded images to PDF or CBZ format."""
    
    @staticmethod
    def get_image_files(images_dir: Path) -> List[Path]:
        """
        Get sorted list of image files in a directory.
        
        Supports: jpg, jpeg, png, webp, gif
        """
        extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        images = [
            f for f in images_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]
        # Sort by filename (assumes numeric naming like 001.jpg)
        images.sort(key=lambda f: f.stem)
        return images
    
    @staticmethod
    def create_pdf(
        images_dir: Path,
        output_path: Path,
        quality: int = 85
    ) -> bool:
        """
        Create a PDF from images in a directory.
        
        Args:
            images_dir: Directory containing images
            output_path: Path for output PDF
            quality: JPEG quality for compression (1-100)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            image_files = FormatConverter.get_image_files(images_dir)
            
            if not image_files:
                logger.error(f"No images found in {images_dir}")
                return False
            
            # Load and convert images
            images: List[Image.Image] = []
            
            for img_path in image_files:
                try:
                    img = Image.open(img_path)
                    # Convert to RGB (required for PDF)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    logger.warning(f"Failed to load image {img_path}: {e}")
            
            if not images:
                logger.error("No valid images to create PDF")
                return False
            
            # Save as PDF
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            first_image = images[0]
            remaining_images = images[1:] if len(images) > 1 else []
            
            first_image.save(
                output_path,
                "PDF",
                save_all=True,
                append_images=remaining_images,
                quality=quality
            )
            
            # Clean up
            for img in images:
                img.close()
            
            logger.debug(f"Created PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PDF: {e}")
            return False
    
    @staticmethod
    def create_cbz(
        images_dir: Path,
        output_path: Path,
        manga_info: Optional[MangaInfo] = None,
        chapter: Optional[Chapter] = None
    ) -> bool:
        """
        Create a CBZ archive from images in a directory.
        
        CBZ is just a ZIP file with images and optional ComicInfo.xml
        
        Args:
            images_dir: Directory containing images
            output_path: Path for output CBZ
            manga_info: Optional manga info for ComicInfo.xml
            chapter: Optional chapter info for ComicInfo.xml
            
        Returns:
            True if successful, False otherwise
        """
        try:
            image_files = FormatConverter.get_image_files(images_dir)
            
            if not image_files:
                logger.error(f"No images found in {images_dir}")
                return False
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
                # Add ComicInfo.xml if we have manga info
                if manga_info and chapter:
                    comicinfo_xml = generate_comicinfo_xml(manga_info, chapter)
                    cbz.writestr("ComicInfo.xml", comicinfo_xml)
                
                # Add images
                for i, img_path in enumerate(image_files, 1):
                    # Keep original extension
                    arc_name = f"{i:03d}{img_path.suffix}"
                    cbz.write(img_path, arc_name)
            
            logger.debug(f"Created CBZ: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create CBZ: {e}")
            return False
