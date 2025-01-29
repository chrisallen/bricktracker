from datetime import datetime, timezone
import csv
import gzip
import logging
import os
from shutil import copyfileobj

from flask import current_app, g
import humanize
import requests

from .exceptions import ErrorException
from .theme import BrickTheme

logger = logging.getLogger(__name__)


# Lego sets themes
class BrickThemeList(object):
    themes: dict[int, BrickTheme]
    mtime: datetime | None
    size: int | None
    exception: Exception | None

    def __init__(self, /, *, force: bool = False):
        # Load themes only if there is none already loaded
        themes = getattr(self, 'themes', None)

        if themes is None or force:
            logger.info('Loading themes list')

            BrickThemeList.themes = {}

            # Try to read the themes from a CSV file
            try:
                with open(current_app.config['THEMES_PATH'], newline='') as themes_file:  # noqa: E501
                    themes_reader = csv.reader(themes_file)

                    # Ignore the header
                    next(themes_reader, None)

                    for row in themes_reader:
                        theme = BrickTheme(*row)
                        BrickThemeList.themes[theme.id] = theme

                # File stats
                stat = os.stat(current_app.config['THEMES_PATH'])
                BrickThemeList.size = stat.st_size
                BrickThemeList.mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)  # noqa: E501

                BrickThemeList.exception = None

            # Ignore errors
            except Exception as e:
                BrickThemeList.exception = e
                BrickThemeList.size = None
                BrickThemeList.mtime = None

    # Get a theme
    def get(self, id: int, /) -> BrickTheme:
        # Seed a fake entry if missing
        if id not in self.themes:
            BrickThemeList.themes[id] = BrickTheme(
                id,
                'Unknown ({id})'.format(id=id)
            )

        return self.themes[id]

    # Display the size in a human format
    def human_size(self) -> str:
        if self.size is not None:
            return humanize.naturalsize(self.size)
        else:
            return ''

    # Display the time in a human format
    def human_time(self) -> str:
        if self.mtime is not None:
            return self.mtime.astimezone(g.timezone).strftime(
                current_app.config['FILE_DATETIME_FORMAT']
            )
        else:
            return ''

    # Update the file
    @staticmethod
    def update() -> None:
        response = requests.get(
            current_app.config['THEMES_FILE_URL'],
            stream=True,
        )

        if not response.ok:
            raise ErrorException('An error occured while downloading the themes file ({code})'.format(  # noqa: E501
                code=response.status_code
            ))

        content = gzip.GzipFile(fileobj=response.raw)

        with open(current_app.config['THEMES_PATH'], 'wb') as f:
            copyfileobj(content, f)

        logger.info('Theme list updated')
