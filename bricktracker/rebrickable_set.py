import logging
import traceback
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from flask import current_app

from .exceptions import ErrorException, NotFoundException
from .rebrickable import Rebrickable
from .rebrickable_image import RebrickableImage
from .rebrickable_minifigures import RebrickableMinifigures
from .rebrickable_parts import RebrickableParts
from .set import BrickSet
from .sql import BrickSQL
from .wish import BrickWish
if TYPE_CHECKING:
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# A set from Rebrickable
class RebrickableSet(object):
    socket: 'BrickSocket'

    def __init__(self, socket: 'BrickSocket', /):
        # Save the socket
        self.socket = socket

    # Import the set from Rebrickable
    def download(self, data: dict[str, Any], /) -> None:
        # Reset the progress
        self.socket.progress_count = 0
        self.socket.progress_total = 0

        # Load the set
        brickset = self.load(data, from_download=True)

        # None brickset means loading failed
        if brickset is None:
            return

        try:
            # Insert into the database
            self.socket.auto_progress(
                message='Set {number}: inserting into database'.format(
                    number=brickset.fields.set_num
                ),
                increment_total=True,
            )

            # Assign a unique ID to the set
            brickset.fields.u_id = str(uuid4())

            # Insert into database
            brickset.insert(commit=False)

            if not current_app.config['USE_REMOTE_IMAGES']:
                RebrickableImage(brickset).download()

            # Load the inventory
            RebrickableParts(self.socket, brickset).download()

            # Load the minifigures
            RebrickableMinifigures(self.socket, brickset).download()

            # Commit the transaction to the database
            self.socket.auto_progress(
                message='Set {number}: writing to the database'.format(
                    number=brickset.fields.set_num
                ),
                increment_total=True,
            )

            BrickSQL().commit()

            # Info
            logger.info('Set {number}: imported (id: {id})'.format(
                number=brickset.fields.set_num,
                id=brickset.fields.u_id,
            ))

            # Complete
            self.socket.complete(
                message='Set {number}: imported (<a href="{url}">Go to the set</a>)'.format(  # noqa: E501
                    number=brickset.fields.set_num,
                    url=brickset.url()
                ),
                download=True
            )

        except Exception as e:
            self.socket.fail(
                message='Error while importing set {number}: {error}'.format(
                    number=brickset.fields.set_num,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

    # Load the set from Rebrickable
    def load(
        self,
        data: dict[str, Any],
        /,
        from_download=False,
    ) -> BrickSet | None:
        # Reset the progress
        self.socket.progress_count = 0
        self.socket.progress_total = 2

        try:
            self.socket.auto_progress(message='Parsing set number')
            set_num = RebrickableSet.parse_number(str(data['set_num']))

            self.socket.auto_progress(
                message='Set {num}: loading from Rebrickable'.format(
                    num=set_num,
                ),
            )

            logger.debug('rebrick.lego.get_set("{set_num}")'.format(
                set_num=set_num,
            ))

            brickset = Rebrickable[BrickSet](
                'get_set',
                set_num,
                BrickSet,
            ).get()

            short = brickset.short()
            short['download'] = from_download

            self.socket.emit('SET_LOADED', short)

            if not from_download:
                self.socket.complete(
                    message='Set {num}: loaded from Rebrickable'.format(
                        num=brickset.fields.set_num
                    )
                )

            return brickset
        except Exception as e:
            self.socket.fail(
                message='Could not load the set from Rebrickable: {error}. Data: {data}'.format(  # noqa: E501
                    error=str(e),
                    data=data,
                )
            )

            if not isinstance(e, (NotFoundException, ErrorException)):
                logger.debug(traceback.format_exc())

        return None

    # Make sense of the number from the data
    @staticmethod
    def parse_number(set_num: str, /) -> str:
        number, _, version = set_num.partition('-')

        # Making sure both are integers
        if version == '':
            version = 1

        try:
            number = int(number)
        except Exception:
            raise ErrorException('Number "{number}" is not a number'.format(
                number=number,
            ))

        try:
            version = int(version)
        except Exception:
            raise ErrorException('Version "{version}" is not a number'.format(
                version=version,
            ))

        # Make sure both are positive
        if number < 0:
            raise ErrorException('Number "{number}" should be positive'.format(
                number=number,
            ))

        if version < 0:
            raise ErrorException('Version "{version}" should be positive'.format(  # noqa: E501
                version=version,
            ))

        return '{number}-{version}'.format(number=number, version=version)

    # Wish from Rebrickable
    # Redefine this one outside of the socket logic
    @staticmethod
    def wish(set_num: str) -> None:
        set_num = RebrickableSet.parse_number(set_num)
        logger.debug('rebrick.lego.get_set("{set_num}")'.format(
            set_num=set_num,
        ))

        brickwish = Rebrickable[BrickWish](
            'get_set',
            set_num,
            BrickWish,
        ).get()

        # Insert into database
        brickwish.insert()

        if not current_app.config['USE_REMOTE_IMAGES']:
            RebrickableImage(brickwish).download()
