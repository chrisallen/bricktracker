from datetime import datetime, timezone
import logging
import os
from urllib.parse import urljoin
from shutil import copyfileobj
import traceback
from typing import Tuple, TYPE_CHECKING

from bs4 import BeautifulSoup
from flask import current_app, g, url_for
import humanize
import requests
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import re
import cloudscraper

from .exceptions import ErrorException, DownloadException
if TYPE_CHECKING:
    from .rebrickable_set import RebrickableSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


class BrickInstructions(object):
    socket: 'BrickSocket'

    allowed: bool
    rebrickable: 'RebrickableSet | None'
    extension: str
    filename: str
    mtime: datetime
    set: 'str | None'
    name: str
    size: int

    def __init__(
        self,
        file: os.DirEntry | str,
        /,
        *,
        socket: 'BrickSocket | None' = None,
    ):
        # Save the socket
        if socket is not None:
            self.socket = socket

        if isinstance(file, str):
            self.filename = file

            if self.filename == '':
                raise ErrorException('An instruction filename cannot be empty')
        else:
            self.filename = file.name

            # Store the file stats
            stat = file.stat()
            self.size = stat.st_size
            self.mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        # Store the name and extension, check if extension is allowed
        self.name, self.extension = os.path.splitext(self.filename)
        self.extension = self.extension.lower()
        self.allowed = self.extension in current_app.config['INSTRUCTIONS_ALLOWED_EXTENSIONS']  # noqa: E501

        # Placeholder
        self.rebrickable = None
        self.set = None

        # Extract the set number
        if self.allowed:
            # Normalize special chars to improve set detection
            normalized = self.name.replace('_', '-')
            normalized = normalized.replace(' ', '-')

            splits = normalized.split('-', 2)

            if len(splits) >= 2:
                try:
                    # Trying to make sense of each part as integers
                    int(splits[0])
                    int(splits[1])

                    self.set = '-'.join(splits[:2])
                except Exception:
                    pass

    # Delete an instruction file
    def delete(self, /) -> None:
        os.remove(self.path())

    # Download an instruction file
    def download(self, path: str, /) -> None:
        """
        Streams the PDF in chunks and uses self.socket.update_total
        + self.socket.progress_count to drive a determinate bar.
        """
        try:
            target = self.path(filename=secure_filename(self.filename))

            # Skip if we already have it
            if os.path.isfile(target):
                return self.socket.complete(
                    message=f"File {self.filename} already exists, skipped"
                )

            # Fetch PDF via cloudscraper (to bypass Cloudflare)
            scraper = cloudscraper.create_scraper()
            scraper.headers.update({
                "User-Agent": current_app.config['REBRICKABLE_USER_AGENT']
            })
            resp = scraper.get(path, stream=True)
            if not resp.ok:
                raise DownloadException(f"Failed to download: HTTP {resp.status_code}")

            # Tell the socket how many bytes in total
            total = int(resp.headers.get("Content-Length", 0))
            self.socket.update_total(total)

            # Reset the counter and kick off at 0%
            self.socket.progress_count = 0
            self.socket.progress(message=f"Starting download {self.filename}")

            # Write out in 8 KiB chunks and update the counter
            with open(target, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)

                    # Bump the internal counter and emit
                    self.socket.progress_count += len(chunk)
                    self.socket.progress(
                        message=(
                            f"Downloading {self.filename} "
                            f"({humanize.naturalsize(self.socket.progress_count)}/"
                            f"{humanize.naturalsize(self.socket.progress_total)})"
                        )
                    )

            # Done!
            logger.info(f"Downloaded {self.filename}")
            self.socket.complete(
                message=f"File {self.filename} downloaded ({self.human_size()})"
            )

        except Exception as e:
            logger.debug(traceback.format_exc())
            self.socket.fail(
                message=f"Error downloading {self.filename}: {e}"
            )

    # Display the size in a human format
    def human_size(self) -> str:
        try:
            size = self.size
        except AttributeError:
            size = os.path.getsize(self.path())
        return humanize.naturalsize(size)

    # Display the time in a human format
    def human_time(self) -> str:
        return self.mtime.astimezone(g.timezone).strftime(
            current_app.config['FILE_DATETIME_FORMAT']
        )

    # Compute the path of an instruction file
    def path(self, /, *, filename=None) -> str:
        if filename is None:
            filename = self.filename

        return os.path.join(
            current_app.static_folder,  # type: ignore
            current_app.config['INSTRUCTIONS_FOLDER'],
            filename
        )

    # Rename an instructions file
    def rename(self, filename: str, /) -> None:
        # Add the extension
        filename = '{name}{ext}'.format(name=filename, ext=self.extension)

        if filename != self.filename:
            # Check if it already exists
            target = self.path(filename=filename)
            if os.path.isfile(target):
                raise ErrorException('Cannot rename {source} to {target} as it already exists'.format(  # noqa: E501
                    source=self.filename,
                    target=filename
                ))

            os.rename(self.path(), target)

    # Upload a new instructions file
    def upload(self, file: FileStorage, /) -> None:
        target = self.path(filename=secure_filename(self.filename))

        if os.path.isfile(target):
            raise ErrorException('Cannot upload {target} as it already exists'.format(  # noqa: E501
                target=self.filename
            ))

        file.save(target)

        # Info
        logger.info('The instruction file {file} has been imported'.format(
            file=self.filename
        ))

    # Compute the url for a set instructions file
    def url(self, /) -> str:
        if not self.allowed:
            return ''

        folder: str = current_app.config['INSTRUCTIONS_FOLDER']

        # Compute the path
        path = os.path.join(folder, self.filename)

        return url_for('static', filename=path)

    # Return the icon depending on the extension
    def icon(self, /) -> str:
        if self.extension == '.pdf':
            return 'file-pdf-2-line'
        elif self.extension in ['.doc', '.docx']:
            return 'file-word-line'
        elif self.extension in ['.png', '.jpg', '.jpeg']:
            return 'file-image-line'
        else:
            return 'file-line'

    # Find the instructions for a set
    @staticmethod
    def find_instructions(set: str, /) -> list[Tuple[str, str]]:
        """
        Scrape Rebrickable’s HTML and return a list of
        (filename_slug, download_url). Duplicate slugs get _1, _2, …
        """
        page_url = f"https://rebrickable.com/instructions/{set}/"
        logger.debug(f"[find_instructions] fetching HTML from {page_url!r}")

        # Solve Cloudflare’s challenge
        scraper = cloudscraper.create_scraper()
        scraper.headers.update({'User-Agent': current_app.config['REBRICKABLE_USER_AGENT']})
        resp = scraper.get(page_url)
        if not resp.ok:
            raise ErrorException(f'Failed to load instructions page for {set}. HTTP {resp.status_code}')

        soup = BeautifulSoup(resp.content, 'html.parser')
        link_re = re.compile(r'^/instructions/\d+/.+/download/')

        raw: list[tuple[str, str]] = []
        for a in soup.find_all('a', href=link_re):
            img = a.find('img', alt=True)
            if not img or set not in img['alt']:
                continue

            # Turn the alt text into a slug
            alt_text = img['alt'].removeprefix('LEGO Building Instructions for ')
            slug = re.sub(r'[^A-Za-z0-9]+', '-', alt_text).strip('-')

            # Build the absolute download URL
            download_url = urljoin('https://rebrickable.com', a['href'])
            raw.append((slug, download_url))

        if not raw:
            raise ErrorException(f'No download links found on instructions page for {set}')

        # Disambiguate duplicate slugs by appending _1, _2, …
        from collections import Counter, defaultdict
        counts = Counter(name for name, _ in raw)
        seen: dict[str, int] = defaultdict(int)
        unique: list[tuple[str, str]] = []
        for name, url in raw:
            idx = seen[name]
            if counts[name] > 1 and idx > 0:
                final_name = f"{name}_{idx}"
            else:
                final_name = name
            seen[name] += 1
            unique.append((final_name, url))

        return unique
