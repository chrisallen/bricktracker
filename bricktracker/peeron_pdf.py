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
                # Create BrickInstructions instance to get PDF URL
                instructions = BrickInstructions(self.filename)
                pdf_url = instructions.url()
                return self.socket.complete(
                    message=f'File {self.filename} already exists, skipped - <a href="{pdf_url}" target="_blank" class="btn btn-sm btn-primary ms-2"><i class="ri-external-link-line"></i> Open PDF</a>'
                )

            # Set up progress tracking
            total_pages = len(self.pages)
            self.socket.update_total(total_pages)
            self.socket.progress_count = 0
            self.socket.progress(message=f"Starting PDF creation from {total_pages} cached pages")

            # Use cached images directly - no downloads needed!
            cached_files_with_rotation = []
            missing_pages = []

            for i, page in enumerate(self.pages):
                # Check if cached file exists
                if os.path.isfile(page.cached_full_image_path):
                    cached_files_with_rotation.append((page.cached_full_image_path, page.rotation))

                    # Update progress
                    self.socket.progress_count += 1
                    self.socket.progress(
                        message=f"Processing cached page {page.page_number} ({i + 1}/{total_pages})"
                    )
                else:
                    missing_pages.append(page.page_number)
                    logger.warning(f"Cached image missing for page {page.page_number}: {page.cached_full_image_path}")

            if not cached_files_with_rotation:
                raise DownloadException(f"No cached images available for set {self.set_number}-{self.version_number}. Cache may have been cleared.")

            elif len(cached_files_with_rotation) < total_pages:
                # Partial success
                error_msg = f"Only found {len(cached_files_with_rotation)}/{total_pages} cached images."
                if missing_pages:
                    error_msg += f" Missing pages: {', '.join(missing_pages)}."
                logger.warning(error_msg)

            # Create PDF from cached images with rotation
            self._create_pdf_from_images(cached_files_with_rotation, target_path)

            # Success
            logger.info(f"Created PDF {self.filename} with {len(cached_files_with_rotation)} pages")

            # Create BrickInstructions instance to get PDF URL
            instructions = BrickInstructions(self.filename)
            pdf_url = instructions.url()

            self.socket.complete(
                message=f'PDF {self.filename} created with {len(cached_files_with_rotation)} pages - <a href="{pdf_url}" target="_blank" class="btn btn-sm btn-primary ms-2"><i class="ri-external-link-line"></i> Open PDF</a>'
            )

            # Clean up set cache after successful PDF creation
            try:
                from .peeron_instructions import clear_set_cache
                deleted_count = clear_set_cache(self.set_number, self.version_number)
                if deleted_count > 0:
                    logger.info(f"[create_pdf] Cleaned up {deleted_count} cache files for set {self.set_number}-{self.version_number}")
            except Exception as e:
                logger.warning(f"[create_pdf] Failed to clean set cache: {e}")

        except Exception as e:
            logger.error(f"Error creating PDF {self.filename}: {e}")
            self.socket.fail(
                message=f"Error creating PDF {self.filename}: {e}"
            )


    # Create PDF from downloaded images
    def _create_pdf_from_images(self, image_paths_and_rotations: list[tuple[str, int]], output_path: str, /) -> None:
        """Create a PDF from a list of image files with their rotations"""
        try:
            # Import FPDF (should be available from requirements)
            from fpdf import FPDF
        except ImportError:
            raise ErrorException("FPDF library not available. Install with: pip install fpdf2")

        pdf = FPDF()

        for i, (img_path, rotation) in enumerate(image_paths_and_rotations):
            try:
                # Open image and apply rotation if needed
                with Image.open(img_path) as image:
                    # Apply rotation if specified
                    if rotation != 0:
                        # PIL rotation is counter-clockwise, so we negate for clockwise rotation
                        image = image.rotate(-rotation, expand=True)

                    width, height = image.size

                    # Add page with image dimensions (convert pixels to mm)
                    # 1 pixel = 0.264583 mm (assuming 96 DPI)
                    page_width = width * 0.264583
                    page_height = height * 0.264583

                    pdf.add_page(format=(page_width, page_height))

                    # Save rotated image to temporary file for FPDF
                    temp_rotated_path = None
                    if rotation != 0:
                        import tempfile
                        temp_fd, temp_rotated_path = tempfile.mkstemp(suffix='.jpg', prefix=f'peeron_rotated_{i}_')
                        try:
                            os.close(temp_fd)  # Close file descriptor, we'll use the path
                            image.save(temp_rotated_path, 'JPEG', quality=95)
                            pdf.image(temp_rotated_path, x=0, y=0, w=page_width, h=page_height)
                        finally:
                            # Clean up rotated temp file
                            if temp_rotated_path and os.path.exists(temp_rotated_path):
                                os.remove(temp_rotated_path)
                    else:
                        pdf.image(img_path, x=0, y=0, w=page_width, h=page_height)

                # Update progress
                progress_msg = f"Processing page {i + 1}/{len(image_paths_and_rotations)} into PDF"
                if rotation != 0:
                    progress_msg += f" (rotated {rotation}°)"
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