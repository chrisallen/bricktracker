import logging
from sqlite3 import Row
from typing import Any, TYPE_CHECKING

from flask import current_app, url_for

from .exceptions import ErrorException
from .rebrickable_image import RebrickableImage
from .record import BrickRecord
if TYPE_CHECKING:
    from .set import BrickSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# A minifigure from Rebrickable
class RebrickableMinifigure(BrickRecord):
    socket: 'BrickSocket'
    brickset: 'BrickSet | None'

    # Queries
    select_query: str = 'rebrickable/minifigure/select'
    insert_query: str = 'rebrickable/minifigure/insert'

    def __init__(
        self,
        /,
        *,
        brickset: 'BrickSet | None' = None,
        socket: 'BrickSocket | None' = None,
        record: Row | dict[str, Any] | None = None
    ):
        super().__init__()

        # Placeholders
        self.instructions = []

        # Save the brickset
        self.brickset = brickset

        # Save the socket
        if socket is not None:
            self.socket = socket

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

    # Insert the minifigure from Rebrickable
    def insert_rebrickable(self, /) -> bool:
        if self.brickset is None:
            raise ErrorException('Importing a minifigure from Rebrickable outside of a set is not supported')  # noqa: E501

        # Insert the Rebrickable minifigure to the database
        rows, _ = self.insert(
            commit=False,
            no_defer=True,
            override_query=RebrickableMinifigure.insert_query
        )

        inserted = rows > 0

        if inserted:
            if not current_app.config['USE_REMOTE_IMAGES']:
                RebrickableImage(
                    self.brickset,
                    minifigure=self,
                ).download()

        return inserted

    # Return a dict with common SQL parameters for a minifigure
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters = super().sql_parameters()

        # Supplement from the brickset
        if self.brickset is not None:
            if 'bricktracker_set_id' not in parameters:
                parameters['bricktracker_set_id'] = self.brickset.fields.id

        return parameters

    # Self url
    def url(self, /) -> str:
        return url_for(
            'minifigure.details',
            figure=self.fields.figure,
        )

    # Compute the url for minifigure image
    def url_for_image(self, /) -> str:
        if not current_app.config['USE_REMOTE_IMAGES']:
            if self.fields.image is None:
                file = RebrickableImage.nil_minifigure_name()
            else:
                file = self.fields.figure

            return RebrickableImage.static_url(file, 'MINIFIGURES_FOLDER')
        else:
            if self.fields.image is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL_MINIFIGURE']
            else:
                return self.fields.image

    # Compute the url for the rebrickable page
    def url_for_rebrickable(self, /) -> str:
        if current_app.config['REBRICKABLE_LINKS']:
            try:
                return current_app.config['REBRICKABLE_LINK_MINIFIGURE_PATTERN'].format(  # noqa: E501
                    number=self.fields.figure,
                )
            except Exception:
                pass

        return ''

    # Normalize from Rebrickable
    @staticmethod
    def from_rebrickable(data: dict[str, Any], /, **_) -> dict[str, Any]:
        # Extracting  number
        number = int(str(data['set_num'])[5:])

        return {
            'figure': str(data['set_num']),
            'number': int(number),
            'name': str(data['set_name']),
            'quantity': int(data['quantity']),
            'image': data['set_img_url'],
        }
