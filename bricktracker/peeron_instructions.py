import hashlib
import logging
import os
from pathlib import Path
import time
from typing import Any, NamedTuple, TYPE_CHECKING
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import cloudscraper
from flask import current_app, url_for
import requests

from .exceptions import ErrorException
if TYPE_CHECKING:
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


def get_peeron_user_agent():
    """Get the User-Agent string for Peeron requests from config"""
    return current_app.config.get('REBRICKABLE_USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')


def get_peeron_download_delay():
    """Get the delay in milliseconds between Peeron page downloads from config"""
    return current_app.config.get('PEERON_DOWNLOAD_DELAY', 1000)


def get_min_image_size():
    """Get the minimum image size for valid Peeron instruction pages from config"""
    return current_app.config.get('PEERON_MIN_IMAGE_SIZE', 100)


def get_peeron_instruction_url(set_number: str, version_number: str):
    """Get the Peeron instruction page URL using the configured pattern"""
    pattern = current_app.config.get('PEERON_INSTRUCTION_PATTERN', 'http://peeron.com/scans/{set_number}-{version_number}')
    return pattern.format(set_number=set_number, version_number=version_number)


def get_peeron_thumbnail_url(set_number: str, version_number: str):
    """Get the Peeron thumbnail base URL using the configured pattern"""
    pattern = current_app.config.get('PEERON_THUMBNAIL_PATTERN', 'http://belay.peeron.com/thumbs/{set_number}-{version_number}/')
    return pattern.format(set_number=set_number, version_number=version_number)


def get_peeron_scan_url(set_number: str, version_number: str):
    """Get the Peeron scan base URL using the configured pattern"""
    pattern = current_app.config.get('PEERON_SCAN_PATTERN', 'http://belay.peeron.com/scans/{set_number}-{version_number}/')
    return pattern.format(set_number=set_number, version_number=version_number)


def create_peeron_scraper():
    """Create a cloudscraper instance configured for Peeron"""
    scraper = cloudscraper.create_scraper()
    scraper.headers.update({
        "User-Agent": get_peeron_user_agent()
    })
    return scraper


def get_thumbnail_cache_dir():
    """Get the directory for thumbnail caching"""
    static_dir = Path(current_app.static_folder)
    cache_dir = static_dir / 'images' / 'peeron_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cached_thumbnail_filename(thumbnail_url: str) -> str:
    """Generate a filename for caching thumbnails based on URL"""
    # Create hash of the URL to avoid filename issues
    url_hash = hashlib.md5(thumbnail_url.encode()).hexdigest()
    # Extract file extension from URL, default to .jpg
    ext = '.jpg'
    if '.' in thumbnail_url:
        url_ext = '.' + thumbnail_url.split('.')[-1].lower()
        if url_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            ext = url_ext
    return f"{url_hash}{ext}"


def cache_thumbnail(thumbnail_url: str) -> str | None:
    """
    Download and cache a thumbnail image, return the local URL path.
    Returns None if caching fails.
    """
    try:
        cache_dir = get_thumbnail_cache_dir()
        filename = get_cached_thumbnail_filename(thumbnail_url)
        cache_path = cache_dir / filename

        # Return existing cached file if it exists
        if cache_path.exists():
            return url_for('static', filename=f'images/peeron_cache/{filename}')

        # Download the thumbnail
        scraper = create_peeron_scraper()
        response = scraper.get(thumbnail_url, timeout=10)

        if response.status_code == 200 and len(response.content) > 0:
            # Validate it's actually an image by checking minimum size
            min_size = get_min_image_size()
            if len(response.content) < min_size:
                logger.warning(f"Thumbnail too small, skipping cache: {thumbnail_url}")
                return None

            # Write to cache
            with open(cache_path, 'wb') as f:
                f.write(response.content)

            logger.debug(f"Cached thumbnail: {thumbnail_url} -> {cache_path}")
            return url_for('static', filename=f'images/peeron_cache/{filename}')
        else:
            logger.warning(f"Failed to download thumbnail: {thumbnail_url}")
            return None

    except Exception as e:
        logger.error(f"Error caching thumbnail {thumbnail_url}: {e}")
        return None


def clear_thumbnail_cache(max_age_days: int = 30) -> int:
    """
    Clear old thumbnail cache files.
    Returns the number of files deleted.
    """
    try:
        cache_dir = get_thumbnail_cache_dir()
        if not cache_dir.exists():
            return 0

        deleted_count = 0
        max_age_seconds = max_age_days * 24 * 60 * 60
        current_time = time.time()

        for cache_file in cache_dir.glob('*'):
            if cache_file.is_file():
                file_age = current_time - os.path.getmtime(cache_file)
                if file_age > max_age_seconds:
                    try:
                        cache_file.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old cache file: {cache_file}")
                    except OSError as e:
                        logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        logger.info(f"Thumbnail cache cleanup completed: {deleted_count} files deleted")
        return deleted_count

    except Exception as e:
        logger.error(f"Error during cache cleanup: {e}")
        return 0


class PeeronPage(NamedTuple):
    """Represents a single instruction page from Peeron"""
    page_number: str
    thumbnail_url: str
    cached_thumbnail_url: str | None  # Local cached thumbnail URL
    image_url: str
    alt_text: str
    rotation: int = 0  # Rotation in degrees (0, 90, 180, 270)


# Peeron instruction scraper
class PeeronInstructions(object):
    socket: 'BrickSocket | None'
    set_number: str
    version_number: str
    pages: list[PeeronPage]

    def __init__(
        self,
        set_number: str,
        version_number: str = '1',
        /,
        *,
        socket: 'BrickSocket | None' = None,
    ):
        # Save the socket
        self.socket = socket

        # Parse set number (handle both "4011" and "4011-1" formats)
        if '-' in set_number:
            parts = set_number.split('-', 1)
            self.set_number = parts[0]
            self.version_number = parts[1] if len(parts) > 1 else '1'
        else:
            self.set_number = set_number
            self.version_number = version_number

        # Placeholder for pages
        self.pages = []

    # Check if instructions exist on Peeron
    def exists(self, /) -> bool:
        """Check if the set exists on Peeron without downloading pages"""
        try:
            pages = self.find_pages()
            return len(pages) > 0
        except ErrorException:
            return False

    # Find all available instruction pages on Peeron
    def find_pages(self, /) -> list[PeeronPage]:
        """
        Scrape Peeron's HTML and return a list of available instruction pages.
        Similar to BrickInstructions.find_instructions() but for Peeron.
        """
        base_url = get_peeron_instruction_url(self.set_number, self.version_number)
        thumb_base_url = get_peeron_thumbnail_url(self.set_number, self.version_number)
        scan_base_url = get_peeron_scan_url(self.set_number, self.version_number)

        logger.debug(f"[find_pages] fetching HTML from {base_url!r}")

        # Set up cloudscraper with cookies enabled for Peeron
        scraper = create_peeron_scraper()

        # Download the main HTML page
        try:
            response = scraper.get(base_url)
            if response.status_code != 200:
                raise ErrorException(f'Failed to load Peeron page for {self.set_number}-{self.version_number}. HTTP {response.status_code}')
        except requests.exceptions.RequestException as e:
            raise ErrorException(f'Failed to connect to Peeron: {e}')

        # Parse HTML to locate instruction pages
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for "Browse instruction library" header (set not found)
        if soup.find('h1', string="Browse instruction library"):
            raise ErrorException(f'Set {self.set_number}-{self.version_number} not found on Peeron')

        # Locate all thumbnail images in the expected table structure
        thumbnails = soup.select('table[cellspacing="5"] a img[src^="http://belay.peeron.com/thumbs/"]')

        if not thumbnails:
            raise ErrorException(f'No instruction pages found for {self.set_number}-{self.version_number} on Peeron')

        pages: list[PeeronPage] = []
        for img in thumbnails:
            thumb_url = img['src']

            # Extract the page number from the thumbnail URL
            page_number = thumb_url.split('/')[-2]

            # Build the full-size image URL
            image_url = f"{scan_base_url}{page_number}/"

            logger.debug(f"[find_pages] Page {page_number}: thumb={thumb_url}, image={image_url}")

            # Create alt text for the page
            alt_text = f"LEGO Instructions {self.set_number}-{self.version_number} Page {page_number}"

            # Cache the thumbnail
            cached_thumb_url = cache_thumbnail(thumb_url)

            page = PeeronPage(
                page_number=page_number,
                thumbnail_url=thumb_url,
                cached_thumbnail_url=cached_thumb_url,
                image_url=image_url,
                alt_text=alt_text
            )
            pages.append(page)

        # Cache the pages for later use
        self.pages = pages

        logger.debug(f"[find_pages] found {len(pages)} pages for {self.set_number}-{self.version_number}")
        return pages

    # Find instructions with fallback to Peeron
    @staticmethod
    def find_instructions_with_peeron_fallback(set: str, /) -> tuple[list[tuple[str, str]], list[PeeronPage] | None]:
        """
        Enhanced version of BrickInstructions.find_instructions() that falls back to Peeron.
        Returns (rebrickable_instructions, peeron_pages).
        If rebrickable_instructions is empty, peeron_pages will contain Peeron data.
        """
        from .instructions import BrickInstructions

        # First try Rebrickable
        try:
            rebrickable_instructions = BrickInstructions.find_instructions(set)
            return rebrickable_instructions, None
        except ErrorException as e:
            logger.info(f"Rebrickable failed for {set}: {e}. Trying Peeron fallback...")

            # Fallback to Peeron
            try:
                peeron = PeeronInstructions(set)
                peeron_pages = peeron.find_pages()
                return [], peeron_pages
            except ErrorException as peeron_error:
                # Both failed, re-raise original Rebrickable error
                logger.info(f"Peeron also failed for {set}: {peeron_error}")
                raise e from peeron_error