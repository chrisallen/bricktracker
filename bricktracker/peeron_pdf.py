import logging
import os
import tempfile
import time
from typing import Any, TYPE_CHECKING

import cloudscraper
from flask import current_app
from PIL import Image

from .exceptions import DownloadException, ErrorException
from .instructions import BrickInstructions
from .peeron_instructions import PeeronPage, get_min_image_size, get_peeron_download_delay, get_peeron_instruction_url, create_peeron_scraper
if TYPE_CHECKING:
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# PDF generator for Peeron instruction pages
class PeeronPDF(object):
    socket: 'BrickSocket'
    set_number: str
    version_number: str
    pages: list[PeeronPage]
    filename: str

    def __init__(
        self,
        set_number: str,
        version_number: str,
        pages: list[PeeronPage],
        /,
        *,
        socket: 'BrickSocket',
    ):
        # Save the socket
        self.socket = socket

        # Save set information
        self.set_number = set_number
        self.version_number = version_number
        self.pages = pages

        # Generate filename following BrickTracker conventions
        self.filename = f"{set_number}-{version_number}_peeron.pdf"

    # Download pages and create PDF
    def create_pdf(self, /) -> None:
        """
        Downloads selected Peeron pages and merges them into a PDF.
        Uses progress updates via socket similar to BrickInstructions.download()
        """
        try:
            target_path = self._get_target_path()

            # Skip if we already have it
            if os.path.isfile(target_path):
                return self.socket.complete(
                    message=f"File {self.filename} already exists, skipped"
                )

            # Set up progress tracking
            total_pages = len(self.pages)
            self.socket.update_total(total_pages)
            self.socket.progress_count = 0
            self.socket.progress(message=f"Starting download of {total_pages} pages")

            # Set up cloudscraper session for all downloads
            scraper = create_peeron_scraper()

            # First visit the main instruction page to establish session with Peeron
            try:
                main_page_url = get_peeron_instruction_url(self.set_number, self.version_number)
                logger.debug(f"Establishing session by visiting: {main_page_url}")
                main_response = scraper.get(main_page_url)
                logger.debug(f"Main page visit: HTTP {main_response.status_code}")
            except Exception as e:
                logger.warning(f"Failed to visit main page: {e}")

            # Download images to temporary files
            temp_files = []
            failed_pages = []

            try:
                for i, page in enumerate(self.pages):
                    # Add delay between requests to avoid being blocked
                    if i > 0:
                        delay_ms = get_peeron_download_delay()
                        time.sleep(delay_ms / 1000.0)  # Convert milliseconds to seconds

                    temp_file = self._download_page_image(page, i + 1, scraper)
                    if temp_file:
                        temp_files.append(temp_file)
                    else:
                        failed_pages.append(page.page_number)

                if not temp_files:
                    # Collect detailed error information
                    error_msg = f"Failed to download any instruction pages for set {self.set_number}-{self.version_number}."

                    # Check if it's a bot protection issue by trying to access the main page
                    try:
                        test_response = scraper.get(get_peeron_instruction_url(self.set_number, self.version_number))
                        if test_response.status_code == 403:
                            error_msg += " Peeron blocked the request (HTTP 403) - bot protection is active."
                        elif test_response.status_code == 404:
                            error_msg += " Set not found on Peeron (HTTP 404)."
                        elif "Browse instruction library" in test_response.text:
                            error_msg += " Set exists on Peeron but has no instruction scans available."
                        else:
                            min_size = get_min_image_size()
                            error_msg += f" All pages returned small error images (smaller than {min_size}x{min_size}) - likely bot protection."
                    except Exception:
                        error_msg += " Could not connect to Peeron - check internet connection."

                    raise DownloadException(error_msg)

                elif len(temp_files) < total_pages:
                    # Partial success
                    error_msg = f"Only downloaded {len(temp_files)}/{total_pages} pages successfully."
                    if failed_pages:
                        error_msg += f" Failed pages: {', '.join(failed_pages)}."
                    logger.warning(error_msg)

                # Create PDF from downloaded images
                self._create_pdf_from_images(temp_files, target_path)

                # Success
                logger.info(f"Created PDF {self.filename} with {len(temp_files)} pages")
                self.socket.complete(
                    message=f"PDF {self.filename} created with {len(temp_files)} pages"
                )

            finally:
                # Cleanup temporary files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        logger.warning(f"Failed to remove temp file {temp_file}: {e}")

        except Exception as e:
            logger.error(f"Error creating PDF {self.filename}: {e}")
            self.socket.fail(
                message=f"Error creating PDF {self.filename}: {e}"
            )

    # Download a single page image
    def _download_page_image(self, page: PeeronPage, page_num: int, scraper, /) -> str | None:
        """Download a single page image to a temporary file using provided scraper session"""
        try:
            logger.debug(f"Attempting to download page {page.page_number} from: {page.image_url}")

            # Download the image using the shared scraper session
            response = scraper.get(page.image_url, stream=True)
            logger.debug(f"Page {page.page_number}: HTTP {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}")

            if not response.ok:
                logger.warning(f"Failed to download page {page.page_number}: HTTP {response.status_code}")
                return None

            # Check if response is actually an image (not an error page)
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                # Log first 500 chars of response for debugging
                try:
                    response_text = response.text[:500]
                    logger.warning(f"Page {page.page_number}: Response is not an image (content-type: {content_type}). Response preview: {response_text}")
                except:
                    logger.warning(f"Page {page.page_number}: Response is not an image (content-type: {content_type})")
                return None

            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg', prefix=f'peeron_{page.page_number}_')

            try:
                with os.fdopen(temp_fd, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Validate that we actually got an image (not an HTML error page)
                try:
                    with Image.open(temp_path) as test_img:
                        width, height = test_img.size
                        min_size = get_min_image_size()
                        if width < min_size or height < min_size:  # Too small to be a real instruction page
                            logger.warning(f"Page {page.page_number}: Image too small ({width}x{height}) - likely an error page")
                            os.remove(temp_path)
                            return None
                except Exception as img_error:
                    logger.warning(f"Page {page.page_number}: Invalid image file - {img_error}")
                    os.remove(temp_path)
                    return None

                # Update progress
                self.socket.progress_count += 1
                self.socket.progress(
                    message=f"Downloaded page {page.page_number} ({page_num}/{len(self.pages)})"
                )

                return temp_path

            except Exception as e:
                # Clean up file descriptor if something went wrong
                try:
                    os.close(temp_fd)
                except:
                    pass
                try:
                    os.remove(temp_path)
                except:
                    pass
                raise e

        except Exception as e:
            logger.warning(f"Failed to download page {page.page_number}: {e}")
            return None

    # Create PDF from downloaded images
    def _create_pdf_from_images(self, image_paths: list[str], output_path: str, /) -> None:
        """Create a PDF from a list of image files"""
        try:
            # Import FPDF (should be available from requirements)
            from fpdf import FPDF
        except ImportError:
            raise ErrorException("FPDF library not available. Install with: pip install fpdf2")

        pdf = FPDF()

        for i, img_path in enumerate(image_paths):
            try:
                # Open image to get dimensions
                with Image.open(img_path) as image:
                    width, height = image.size

                # Add page with image dimensions (convert pixels to mm)
                # 1 pixel = 0.264583 mm (assuming 96 DPI)
                page_width = width * 0.264583
                page_height = height * 0.264583

                pdf.add_page(format=(page_width, page_height))
                pdf.image(img_path, x=0, y=0, w=page_width, h=page_height)

                # Update progress
                progress_msg = f"Processing page {i + 1}/{len(image_paths)} into PDF"
                self.socket.progress(message=progress_msg)

            except Exception as e:
                logger.warning(f"Failed to add image {img_path} to PDF: {e}")
                continue

        # Save the PDF
        pdf.output(output_path)

    # Get target file path
    def _get_target_path(self, /) -> str:
        """Get the full path where the PDF should be saved"""
        instructions_folder = os.path.join(
            current_app.static_folder,  # type: ignore
            current_app.config['INSTRUCTIONS_FOLDER']
        )
        return os.path.join(instructions_folder, self.filename)

    # Create BrickInstructions instance for the generated PDF
    def get_instructions(self, /) -> BrickInstructions:
        """Return a BrickInstructions instance for the generated PDF"""
        return BrickInstructions(self.filename)