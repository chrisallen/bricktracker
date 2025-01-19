import logging
from typing import TYPE_CHECKING

from flask import current_app

from .minifigure import BrickMinifigure
from .rebrickable import Rebrickable
from .rebrickable_image import RebrickableImage
from .rebrickable_parts import RebrickableParts
if TYPE_CHECKING:
    from .set import BrickSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# Minifigures from Rebrickable
class RebrickableMinifigures(object):
    socket: 'BrickSocket'
    brickset: 'BrickSet'

    def __init__(self, socket: 'BrickSocket', brickset: 'BrickSet', /):
        # Save the socket
        self.socket = socket

        # Save the objects
        self.brickset = brickset

    # Import the minifigures from Rebrickable
    def download(self, /) -> None:
        self.socket.auto_progress(
            message='Set {number}: loading minifigures from Rebrickable'.format(  # noqa: E501
                number=self.brickset.fields.set_num,
            ),
            increment_total=True,
        )

        logger.debug('rebrick.lego.get_set_minifigs("{set_num}")'.format(
            set_num=self.brickset.fields.set_num,
        ))

        minifigures = Rebrickable[BrickMinifigure](
            'get_set_minifigs',
            self.brickset.fields.set_num,
            BrickMinifigure,
            socket=self.socket,
            brickset=self.brickset,
        ).list()

        # Process each minifigure
        total = len(minifigures)
        for index, minifigure in enumerate(minifigures):
            # Insert into the database
            self.socket.auto_progress(
                message='Set {number}: inserting minifigure {current}/{total} into database'.format(  # noqa: E501
                    number=self.brickset.fields.set_num,
                    current=index+1,
                    total=total,
                )
            )

            # Insert into database
            minifigure.insert(commit=False)

            # Grab the image
            self.socket.progress(
                message='Set {number}: downloading minifigure {current}/{total} image'.format(  # noqa: E501
                    number=self.brickset.fields.set_num,
                    current=index+1,
                    total=total,
                )
            )

            if not current_app.config['USE_REMOTE_IMAGES'].value:
                RebrickableImage(
                    self.brickset,
                    minifigure=minifigure
                ).download()

            # Load the inventory
            RebrickableParts(
                self.socket,
                self.brickset,
                minifigure=minifigure,
            ).download()
