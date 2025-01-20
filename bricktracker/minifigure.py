from sqlite3 import Row
from typing import Any, Self, TYPE_CHECKING

from flask import current_app, url_for

from .exceptions import ErrorException, NotFoundException
from .part_list import BrickPartList
from .rebrickable_image import RebrickableImage
from .record import BrickRecord
if TYPE_CHECKING:
    from .set import BrickSet


# Lego minifigure
class BrickMinifigure(BrickRecord):
    brickset: 'BrickSet | None'

    # Queries
    insert_query: str = 'minifigure/insert'
    generic_query: str = 'minifigure/select/generic'
    select_query: str = 'minifigure/select/specific'

    def __init__(
        self,
        /,
        brickset: 'BrickSet | None' = None,
        record: Row | dict[str, Any] | None = None,
    ):
        super().__init__()

        # Save the brickset
        self.brickset = brickset

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

    # Return the number just in digits format
    def clean_number(self, /) -> str:
        number: str = self.fields.fig_num
        number = number.removeprefix('fig-')
        number = number.lstrip('0')

        return number

    # Parts
    def generic_parts(self, /) -> BrickPartList:
        return BrickPartList().from_minifigure(self)

    # Parts
    def parts(self, /) -> BrickPartList:
        if self.brickset is None:
            raise ErrorException('Part list for minifigure {number} requires a brickset'.format(  # noqa: E501
                number=self.fields.fig_num,
            ))

        return BrickPartList().load(self.brickset, minifigure=self)

    # Select a generic minifigure
    def select_generic(self, fig_num: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.fig_num = fig_num

        record = self.select(override_query=self.generic_query)

        if record is None:
            raise NotFoundException(
                'Minifigure with number {number} was not found in the database'.format(  # noqa: E501
                    number=self.fields.fig_num,
                ),
            )

        # Ingest the record
        self.ingest(record)

        return self

    # Select a specific minifigure (with a set and an number)
    def select_specific(self, brickset: 'BrickSet', fig_num: str, /) -> Self:
        # Save the parameters to the fields
        self.brickset = brickset
        self.fields.fig_num = fig_num

        record = self.select()

        if record is None:
            raise NotFoundException(
                'Minifigure with number {number} from set {set} was not found in the database'.format(  # noqa: E501
                    number=self.fields.fig_num,
                    set=self.brickset.fields.set_num,
                ),
            )

        # Ingest the record
        self.ingest(record)

        return self

    # Return a dict with common SQL parameters for a minifigure
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters = super().sql_parameters()

        # Supplement from the brickset
        if self.brickset is not None:
            if 'u_id' not in parameters:
                parameters['u_id'] = self.brickset.fields.u_id

            if 'set_num' not in parameters:
                parameters['set_num'] = self.brickset.fields.set_num

        return parameters

    # Self url
    def url(self, /) -> str:
        return url_for(
            'minifigure.details',
            number=self.fields.fig_num,
        )

    # Compute the url for minifigure part image
    def url_for_image(self, /) -> str:
        if not current_app.config['USE_REMOTE_IMAGES']:
            if self.fields.set_img_url is None:
                file = RebrickableImage.nil_minifigure_name()
            else:
                file = self.fields.fig_num

            return RebrickableImage.static_url(file, 'MINIFIGURES_FOLDER')
        else:
            if self.fields.set_img_url is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL_MINIFIGURE']
            else:
                return self.fields.set_img_url

    # Compute the url for the rebrickable page
    def url_for_rebrickable(self, /) -> str:
        if current_app.config['REBRICKABLE_LINKS']:
            try:
                return current_app.config['REBRICKABLE_LINK_MINIFIGURE_PATTERN'].format(  # noqa: E501
                    number=self.fields.fig_num.lower(),
                )
            except Exception:
                pass

        return ''

    # Normalize from Rebrickable
    @staticmethod
    def from_rebrickable(
        data: dict[str, Any],
        /,
        brickset: 'BrickSet | None' = None,
        **_,
    ) -> dict[str, Any]:
        record = {
            'fig_num': data['set_num'],
            'name': data['set_name'],
            'quantity': data['quantity'],
            'set_img_url': data['set_img_url'],
        }

        if brickset is not None:
            record['set_num'] = brickset.fields.set_num
            record['u_id'] = brickset.fields.u_id

        return record
