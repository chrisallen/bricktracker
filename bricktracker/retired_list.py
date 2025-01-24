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
from .retired import BrickRetired

logger = logging.getLogger(__name__)


# Lego retired sets
class BrickRetiredList(object):
    retired: dict[str, BrickRetired]
    mtime: datetime | None
    size: int | None
    exception: Exception | None

    def __init__(self, /, *, force: bool = False):
        # Load sets only if there is none already loaded
        retired = getattr(self, 'retired', None)

        if retired is None or force:
            logger.info('Loading retired sets list')

            BrickRetiredList.retired = {}

            # Try to read the themes from a CSV file
            try:
                with open(current_app.config['RETIRED_SETS_PATH'], newline='') as themes_file:  # noqa: E501
                    themes_reader = csv.reader(themes_file)

                    # Ignore the header
                    next(themes_reader, None)

                    for row in themes_reader:
                        retired = BrickRetired(*row)
                        BrickRetiredList.retired[retired.number] = retired

                # File stats
                stat = os.stat(current_app.config['RETIRED_SETS_PATH'])
                BrickRetiredList.size = stat.st_size
                BrickRetiredList.mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)  # noqa: E501

                BrickRetiredList.exception = None

            # Ignore errors
            except Exception as e:
                BrickRetiredList.exception = e
                BrickRetiredList.size = None
                BrickRetiredList.mtime = None

    # Get a retirement date for a set
    def get(self, number: str, /) -> str:
        if number in self.retired:
            return self.retired[number].retirement_date
        else:
            number, _, _ = number.partition('-')

            if number in self.retired:
                return self.retired[number].retirement_date
            else:
                return ''

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
            current_app.config['RETIRED_SETS_FILE_URL'],
            stream=True,
        )

        if not response.ok:
            raise ErrorException('An error occured while downloading the retired sets file ({code})'.format(  # noqa: E501
                code=response.status_code
            ))

        content = gzip.GzipFile(fileobj=response.raw)

        with open(current_app.config['RETIRED_SETS_PATH'], 'wb') as f:
            copyfileobj(content, f)

    logger.info('Retired sets list updated')
