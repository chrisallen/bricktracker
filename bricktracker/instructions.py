from datetime import datetime, timezone
import logging
import os
from shutil import copyfileobj
import traceback
from typing import Tuple, TYPE_CHECKING

from bs4 import BeautifulSoup
from flask import current_app, g, url_for
import humanize
import requests
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

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
        try:
            # Just to make sure that the progress is initiated
            self.socket.progress(
                message='Downloading {file}'.format(
                    file=self.filename,
                )
            )

            target = self.path(filename=secure_filename(self.filename))

            # Skipping rather than failing here
            if os.path.isfile(target):
                self.socket.complete(
                    message='File {file} already exists, skipped'.format(
                        file=self.filename,
                    )
                )

            else:
                url = current_app.config['REBRICKABLE_LINK_INSTRUCTIONS_PATTERN'].format(  # noqa: E501
                    path=path
                )
                trimmed_url = current_app.config['REBRICKABLE_LINK_INSTRUCTIONS_PATTERN'].format(  # noqa: E501
                    path=path.partition('/')[0]
                )

                # Request the file
                self.socket.progress(
                    message='Requesting {url}'.format(
                        url=trimmed_url,
                    )
                )

                response = requests.get(url, stream=True)
                if response.ok:

                    # Store the content header as size
                    try:
                        self.size = int(
                            response.headers.get('Content-length', 0)
                        )
                    except Exception:
                        self.size = 0

                    # Downloading the file
                    self.socket.progress(
                        message='Downloading {url} ({size})'.format(
                            url=trimmed_url,
                            size=self.human_size(),
                        )
                    )

                    with open(target, 'wb') as f:
                        copyfileobj(response.raw, f)
                else:
                    raise DownloadException('failed to download: {code}'.format(  # noqa: E501
                        code=response.status_code
                    ))

                # Info
                logger.info('The instruction file {file} has been downloaded'.format(  # noqa: E501
                    file=self.filename
                ))

                # Complete
                self.socket.complete(
                    message='File {file} downloaded ({size})'.format(  # noqa: E501
                        file=self.filename,
                        size=self.human_size()
                    )
                )

        except Exception as e:
            self.socket.fail(
                message='Error while downloading instruction {file}: {error}'.format(  # noqa: E501
                    file=self.filename,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

    # Display the size in a human format
    def human_size(self) -> str:
        return humanize.naturalsize(self.size)

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
        response = requests.get(
            current_app.config['REBRICKABLE_LINK_INSTRUCTIONS_PATTERN'].format(
                path=set,
            ),
            headers={
                'User-Agent': current_app.config['REBRICKABLE_USER_AGENT']
            }
        )

        if not response.ok:
            raise ErrorException('Failed to load the Rebrickable instructions page. Status code: {code}'.format(  # noqa: E501
                code=response.status_code
            ))

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Collect all <img> tags with "LEGO Building Instructions" in the
        # alt attribute
        found_tags: list[Tuple[str, str]] = []
        for a_tag in soup.find_all('a', href=True):
            img_tag = a_tag.find('img', alt=True)
            if img_tag and "LEGO Building Instructions" in img_tag['alt']:
                found_tags.append(
                    (
                        img_tag['alt'].removeprefix('LEGO Building Instructions for '),  # noqa: E501
                        a_tag['href']
                    )
                )  # Save alt and href

        # Raise an error if nothing found
        if not len(found_tags):
            raise ErrorException('No instruction found for set {set}'.format(
                set=set
            ))

        return found_tags
