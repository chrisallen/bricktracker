import logging
from typing import TYPE_CHECKING

from flask import current_app

from .part import BrickPart
from .rebrickable import Rebrickable
from .rebrickable_image import RebrickableImage
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .set import BrickSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# A list of parts from Rebrickable
class RebrickableParts(object):
    socket: 'BrickSocket'
    brickset: 'BrickSet'
    minifigure: 'BrickMinifigure | None'

    number: str
    kind: str
    method: str

    def __init__(
        self,
        socket: 'BrickSocket',
        brickset: 'BrickSet',
        /,
        minifigure: 'BrickMinifigure | None' = None,
    ):
        # Save the socket
        self.socket = socket

        # Save the objects
        self.brickset = brickset
        self.minifigure = minifigure

        if self.minifigure is not None:
            self.number = self.minifigure.fields.fig_num
            self.kind = 'Minifigure'
            self.method = 'get_minifig_elements'
        else:
            self.number = self.brickset.fields.set_num
            self.kind = 'Set'
            self.method = 'get_set_elements'

    # Import the parts from Rebrickable
    def download(self, /) -> None:
        self.socket.auto_progress(
            message='{kind} {number}: loading parts inventory from Rebrickable'.format(  # noqa: E501
                kind=self.kind,
                number=self.number,
            ),
            increment_total=True,
        )

        logger.debug('rebrick.lego.{method}("{number}")'.format(
            method=self.method,
            number=self.number,
        ))

        inventory = Rebrickable[BrickPart](
            self.method,
            self.number,
            BrickPart,
            socket=self.socket,
            brickset=self.brickset,
            minifigure=self.minifigure,
        ).list()

        # Process each part
        total = len(inventory)
        for index, part in enumerate(inventory):
            # Skip spare parts
            if (
                current_app.config['SKIP_SPARE_PARTS'] and
                part.fields.is_spare
            ):
                continue

            # Insert into the database
            self.socket.auto_progress(
                message='{kind} {number}: inserting part {current}/{total} into database'.format(  # noqa: E501
                    kind=self.kind,
                    number=self.number,
                    current=index+1,
                    total=total,
                )
            )

            # Insert into database
            part.insert(commit=False)

            # Grab the image
            self.socket.progress(
                message='{kind} {number}: downloading part {current}/{total} image'.format(  # noqa: E501
                    kind=self.kind,
                    number=self.number,
                    current=index+1,
                    total=total,
                )
            )

            if not current_app.config['USE_REMOTE_IMAGES']:
                RebrickableImage(
                    self.brickset,
                    minifigure=self.minifigure,
                    part=part,
                ).download()
